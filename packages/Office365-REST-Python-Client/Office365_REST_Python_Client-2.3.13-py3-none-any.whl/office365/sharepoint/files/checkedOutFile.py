from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.internal.paths.entity import EntityPath
from office365.sharepoint.principal.user import User


class CheckedOutFile(BaseEntity):
    """Represents a checked-out file in a document library or workspace."""

    @property
    def checked_out_by_id(self):
        """Returns the user ID of the account used to check out the file.

        :rtype: int or None
        """
        return self.get_property("CheckedOutById", None)

    @property
    def checked_out_by(self):
        """Returns the user name of the account used to check out the file."""
        return self.properties.get('CheckedOutBy',
                                   User(self.context, ResourcePath("CheckedOutBy", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "CheckedOutBy": self.checked_out_by
            }
            default_value = property_mapping.get(name, None)
        return super(CheckedOutFile, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(CheckedOutFile, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "CheckedOutById":
            self._resource_path = EntityPath(value, self.parent_collection.resource_path)
