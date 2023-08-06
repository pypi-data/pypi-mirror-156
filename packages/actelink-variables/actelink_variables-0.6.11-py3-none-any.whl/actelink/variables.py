import requests
import urllib.parse
from os import getenv
import time
from actelink.logger import log
from actelink.models import Context

_stores     = dict()
_session    = None
_cache_date = 0

def init(url: str = None, key: str = None):
    """Initialise le module actelink.variables

    :param str url: L'url de connexion au moteur de varibales.
    :param str key: La clé d'API avec laquelle s'authentifier auprès du moteur de variables.

    :raises ConnectionError: en cas d'échec de connexion au moteur de variables.
    """
    # use variable engine url & api-key from environment variables by default
    var_url = getenv("VARIABLE_ENGINE_URL", url)
    var_key = getenv("VARIABLE_ENGINE_API_KEY", key)
    log.info(f"call variables engine with url: {var_url}, key: {var_key}")
    global __VARIABLES_ENDPOINT, __STORES_ENDPOINT, __CACHE_ENABLED, __CACHE_TTL, _stores, _session
    __CACHE_ENABLED      = getenv("CACHE_ENABLED", True)
    __CACHE_TTL          = int(getenv("CACHE_TTL", 10))
    __VARIABLES_ENDPOINT = urllib.parse.urljoin(var_url, "/api/v1/stores/{storeId}/variables/{label}")
    __STORES_ENDPOINT    = urllib.parse.urljoin(var_url, "/api/v1/stores")
    _session = requests.Session()
    _session.headers.update({"api-key": var_key})
    __build_cache()

def __build_cache():
    global _cache_date
    # do nothing if last cache update occured less than __CACHE_TTL sec. ago
    if time.time() < (_cache_date + __CACHE_TTL):
        return
    log.info(f"update cache")
    # retrieve the list of stores for this customer
    try:
        response = _session.get(__STORES_ENDPOINT)
    except requests.exceptions.ConnectionError as error:
        log.error(f"CONNECTION FAILED!\n\n{error})")
        raise
    # check response is valid
    if response.status_code != 200:
        raise requests.exceptions.ConnectionError(f"Cache building failed, reason: {response.reason}")
    elif response.json() is None:
        log.warn("Warning: no stores found")
    else:
        for store in response.json():
            context = Context.from_string(store["name"])
            if context is not None:
                # cache variables of current store
                if store["variables"] is not None:
                    # convert list of variables into a dict {var_label:var_object}
                    variables = { store["variables"][idx]["label"]:var for idx, var in enumerate(store["variables"]) }
                else:
                    variables = {}
                # fill our stores map with context as key
                _stores[context] = {"id": store["id"], "name": store["name"], "variables": variables}
                log.debug(f"found store {store['name']} (id {store['id']})")
            else:
                log.error(f"invalid store name \'{store['name']}\' (id {store['id']})")
        log.info(f"done")
        _cache_date = time.time()

def get_stores() -> tuple:
    """Retourne les stores existants sous forme d'un tuple.
    
    :returns: Un tuple contenant l'ensemble des stores associés à votre clé d'API.
    :rtype: tuple
    """
    return tuple((store['name']) for store in _stores.values())

def __context_to_store(context: Context) -> dict:
    try:
        store = _stores[context]
    except KeyError:
        log.error(f"no store found for {context}")
        raise
    return store

def __get_from_cache(variable: object, requested_keys):
    # update cache if needed
    __build_cache()
    # d0 variable, ex: keys = [], values = [0.5]
    if requested_keys is None:
        return variable["values"][0]
    else:
        keys = variable["keys"]
        # d1 variable, ex: keys = ["key1", "key2"], values = [0.5, 0.6]
        if variable["type"] == "d1":
            try:
                idx = keys.index(requested_keys)
            except ValueError:
                log.error(f"key {requested_keys} does not exist")
                raise KeyError
            return variable["values"][idx]
        # d2 variable, ex: keys = [["key1_1","key1_2"],["key2_1","key2_2"]], values = [[0.5,0.6],[0.7,0.8]]
        # value for "key1_2, key2_2" -> values[1][1] -> 0.8
        elif variable["type"] == "d2":
            # requested keys can be passed as a list or a comma separated string
            if isinstance(requested_keys, str):
                requested_keys = requested_keys.split(",")
            keys_idx = []
            # we only handle two dimensional arrays
            for i in range(2):
                try:
                    # TODO: handle case where client gives keys in the wrong order?
                    idx_key = keys[i].index(requested_keys[i])
                    keys_idx.append(idx_key)
                except ValueError:
                    log.error(f"key {requested_keys[i]} does not exist")
                    raise KeyError
            return variable["values"][keys_idx[0]][keys_idx[1]]
        else:
            raise KeyError

def get_variable(context: Context, var_label: str, var_keys=None):
    """Retourne la valeur d'une variable dans un contexte donné.

    :param Context context: Le contexte dans lequel on demande cette variable.
    :param str var_label: Le nom de la variable à retourner.
    :param str var_keys: La ou les clés à spécifier pour cette variable (None par défaut).
    :type var_keys: str or list or None

    :returns: La valeur de la variable *var_label* pour la/les clé(s) donnée(s) si spécifiée(s).
    :rtype: float or str
    :raises KeyError: si le contexte donné ou la variable n'existe pas.
    :raises ConnectionError: si un problème de connexion est survenue avec le moteur de variables

    Exemples d'utilisation :

    * Cas d'une variable d0

    >>> import actelink.variables as av
    >>> from actelink.models import Context, Calcul

    >>> context = Context(...)
    >>> intercept = av.get_variable(context, 'intercept')
    >>> print(intercept)
    0.893

    * Cas d'une variable d1
    
    >>> niveau = av.get_variable(context, 'niveau', 'medium')
    >>> print(niveau)
    0.24

    * Cas d'une variable d2
    
    >>> situation = av.get_variable(context, 'situation', 'homme,celibataire')
    >>> print(situation)
    0.893

    .. NOTE:: Dans le cas d'une variable de type d2, où deux clés doivent être spécifiées, celles ci peuvent être passées en paramètre sous la forme d'une string ou d'une liste :
    
    >>> situation = av.get_variable(context, 'situation', 'homme,celibataire')

    est équivalent à :

    >>> situation = av.get_variable(context, 'situation', ['homme', 'celibataire'])
    """
    store = __context_to_store(context)
    log.info(f"{var_label} on store {store['id']}, requested key: {var_keys}")
    # get variable from cache
    if __CACHE_ENABLED:
        if store["variables"] is None or store["variables"][var_label] is None:
            log.error(f"{var_label} does not exist")
            raise KeyError            
        return __get_from_cache(store["variables"][var_label], var_keys)
    # get variable from endpoint
    url = __VARIABLES_ENDPOINT.replace("{storeId}", store['id']).replace("{label}", var_label)
    # var_keys can be passed as a string or array of strings
    var_keys = ",".join(k.strip() for k in var_keys) if isinstance(var_keys, list) else var_keys
    try:
        response = _session.get(url, params={"key": var_keys})
    except requests.exceptions.ConnectionError as error:
        log.error(f"GET {url} FAILED\n\n{error})")
        raise
    if response.status_code != 200:
        log.error(f"GET {url} failed, reason: {response.reason}")
        raise KeyError(f"GET {url} failed, reason: {response.reason}")
    #log.debug(f"GET {url} Compute-Time: {response.headers["Compute-Time"]}")
    return response.json()

def get_variables(context: Context) -> list:
    """Retourne la liste de toutes les variables d'un contexte (store) donné.

    :param Context context: Le contexte pour lequel on veut récupérer la liste de variables.

    :returns: La liste des variables du contexte donné.
    :rtype: list

    Exemples d'utilisation :

    >>> context = Context(...)
    >>> all_vars = av.get_variables(context)
    """
    store = __context_to_store(context)
    try:
        response = _session.get(__STORES_ENDPOINT)
    except requests.exceptions.ConnectionError as error:
        log.error(f"GET {__STORES_ENDPOINT} failed\n\n{error})")
        raise
    # check response is valid
    if response.status_code != 200:
        raise requests.exceptions.ConnectionError(f"GET {__STORES_ENDPOINT} failed, reason: {response.reason}")
    store = next(s for s in response.json() if s["id"] == store["id"])
    return store["variables"]
