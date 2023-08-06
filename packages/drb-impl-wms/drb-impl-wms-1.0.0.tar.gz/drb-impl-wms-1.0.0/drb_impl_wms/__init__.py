from . import _version
from .wms_nodes import WmsServiceNode, WXSNodeOperationGetMap, \
    WXSNodeOperationGetFeatureInfo, WmsGetMapPredicate, \
    WmsGetFeatureInfoPredicate

__version__ = _version.get_versions()['version']
__all__ = [
    'WmsServiceNode',
    'WXSNodeOperationGetMap',
    'WXSNodeOperationGetFeatureInfo',
    'WmsGetMapPredicate',
    'WmsGetFeatureInfoPredicate']
