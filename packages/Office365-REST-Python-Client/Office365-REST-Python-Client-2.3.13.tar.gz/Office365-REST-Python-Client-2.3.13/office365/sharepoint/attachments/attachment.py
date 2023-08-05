from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.internal.queries.download_file import create_download_file_query
from office365.sharepoint.internal.queries.upload_file import create_upload_file_query
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class Attachment(BaseEntity):
    """Represents an attachment file in a SharePoint List Item."""

    def download(self, file_object, use_path=True):
        """Download attachment file content

        :type file_object: typing.IO
        :param bool use_path: Use Path instead of Url for addressing attachments
        """

        def _download_file_by_path():
            file = self.context.web.get_file_by_server_relative_path(self.server_relative_path)
            qry = create_download_file_query(file, file_object)
            self.context.add_query(qry)

        def _download_file_by_url():
            file = self.context.web.get_file_by_server_relative_url(self.server_relative_url)
            qry = create_download_file_query(file, file_object)
            self.context.add_query(qry)

        if use_path:
            self.ensure_property("ServerRelativePath", _download_file_by_path)
        else:
            self.ensure_property("ServerRelativeUrl", _download_file_by_url)
        return self

    def upload(self, file_object, use_path=True):
        """
        Upload attachment into list item

        :type file_object: typing.IO
        :param bool use_path: Use Path instead of Url for addressing attachments
        """

        def _upload_file_by_url():
            target_file = self.context.web.get_file_by_server_relative_url(self.server_relative_url)
            qry = create_upload_file_query(target_file, file_object)
            self.context.add_query(qry)

        def _upload_file_by_path():
            target_file = self.context.web.get_file_by_server_relative_path(self.server_relative_path)
            qry = create_upload_file_query(target_file, file_object)
            self.context.add_query(qry)

        if use_path:
            self.ensure_property("ServerRelativePath", _upload_file_by_path)
        else:
            self.ensure_property("ServerRelativeUrl", _upload_file_by_url)
        return self

    @property
    def file_name(self):
        """
        Specifies the file name of the list item attachment.

        :rtype: str or None
        """
        return self.properties.get("FileName", None)

    @property
    def file_name_as_path(self):
        """
        The file name of the attachment as a SP.ResourcePath.
        """
        return self.properties.get("FileNameAsPath", SPResPath())

    @property
    def server_relative_url(self):
        """
        :rtype: str or None
        """
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def server_relative_path(self):
        """
        The server-relative-path of the attachment.
        """
        return self.properties.get("ServerRelativePath", SPResPath())

    def set_property(self, name, value, persist_changes=True):
        super(Attachment, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "ServerRelativeUrl":
                self._resource_path = self.context.web.get_file_by_server_relative_url(value).resource_path

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "FileNameAsPath": self.file_name_as_path,
                "ServerRelativePath": self.server_relative_path,
            }
            default_value = property_mapping.get(name, None)
        return super(Attachment, self).get_property(name, default_value)
