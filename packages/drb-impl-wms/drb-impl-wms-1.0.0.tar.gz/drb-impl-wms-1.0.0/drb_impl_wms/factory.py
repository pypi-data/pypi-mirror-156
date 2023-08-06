import io
import json

from drb import DrbNode
from drb.factory import DrbFactory
from drb_impl_http import DrbHttpNode
from drb_impl_json import JsonNode

from .wms_nodes import WmsServiceNode


class WmsFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbHttpNode):
            return WmsServiceNode(source=node.path.original_path,
                                  auth=node.auth)
        return WmsServiceNode(node.path.name)
