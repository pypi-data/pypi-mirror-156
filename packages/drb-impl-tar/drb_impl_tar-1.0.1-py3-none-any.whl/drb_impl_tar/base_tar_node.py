import io
import tarfile
from typing import Any, Dict, Tuple, Optional

from drb import DrbNode
from drb.factory import DrbFactory
from drb.path import ParsedPath
from .execptions import DrbTarNodeException
from .tar_node import DrbTarNode


class DrbBaseTarNode(DrbTarNode):
    """
    This node is used to open a tar container, and browse his content.

    Parameters:
        base_node (DrbNode): The base node.
    """
    def __init__(self, base_node: DrbNode):
        super().__init__(parent=base_node.parent, tar_info=None)
        self._all_members = None
        self._tar_file = None
        self.base_node = base_node
        self._tar_file_source = None

    @property
    def parent(self) -> Optional[DrbNode]:
        """
        Returns the parent of the base node.

        Returns:
            DrbNode: the parent of the node
        """
        return self.base_node.parent

    @property
    def path(self) -> ParsedPath:
        """
        Returns the path of the base node.

        Returns:
            ParsedPath: the full path of the base node
        """
        return self.base_node.path

    @property
    def name(self) -> str:
        """
        Return the name of the base node.
        This name doesn't contain the path.

        Returns:
            str: the base node name
        """
        return self.base_node.name

    @property
    def namespace_uri(self) -> Optional[str]:
        """
        Return the namespace uri of the base node.

        Returns:
            str: the base node namespace
        """
        return self.base_node.namespace_uri

    @property
    def value(self) -> Optional[Any]:
        """
        Return the value of the base node.

        Returns:
            Any: the value
        """
        return self.base_node.value

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        """
        Return the attributes of the base node.

        Returns:
            Dict: Key(key_name, key_namespace): value(Any)
        """
        return self.base_node.attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        """
        Return a specific attributes of the base node.

        Parameters:
            name (str): The name of the attribute.
            namespace_uri (str): The namespace_uri of the attribute
                                 (default: None).
        Returns:
            Any: the attribute
        """
        return self.base_node.get_attribute(name, namespace_uri)

    @property
    def tar_file(self) -> tarfile.TarFile:
        if self._tar_file is None:
            try:

                if self.base_node.has_impl(io.BufferedIOBase):
                    self._tar_file_source = self.base_node \
                        .get_impl(io.BufferedIOBase)
                    # If the impl is not seekable
                    # it creates a ByteIO with the entire buff
                    if not self._tar_file_source.seekable():
                        self._tar_file_source = io.BytesIO(
                            self._tar_file_source.read())
                    self._tar_file = tarfile.TarFile(fileobj=self
                                                     ._tar_file_source)
                else:
                    raise DrbTarNodeException(
                        f'Unsupported base_node'
                        f' {type(self.base_node).__name__} '
                        f'for DrbFileTarNode')
            except Exception as e:
                raise DrbTarNodeException(f'Unable to read tar file'
                                          f' {self.name} ') from e

        return self._tar_file

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type, **kwargs) -> Any:
        return self.base_node.get_impl(impl)

    def get_members(self):
        if self._all_members is None:
            self._all_members = self.tar_file.getmembers()
        return self._all_members

    def _is_a_child(self, filename):

        # chek if this entries is a child or a sub child if yes => not a child
        # of the root
        if any(filename.startswith(name_entry) and filename != name_entry
               for name_entry in self.tar_file.getnames()):
            return False
        return True

    def open_member(self, tar_info: tarfile.TarInfo):
        # open a member of the tar en return an BufferedIOBase impl
        return self._tar_file.extractfile(tar_info)

    def close(self):
        if self._tar_file_source is not None:
            self._tar_file_source.close()
        if self._tar_file is not None:
            self._tar_file.close()
        self.base_node.close()


class DrbTarFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        return DrbBaseTarNode(base_node=node)
