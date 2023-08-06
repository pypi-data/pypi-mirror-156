__all__ = ('MessageInteraction',)

from scarletio import include

from ..bases import DiscordEntity
from ..user import User


InteractionType = include('InteractionType')


class MessageInteraction(DiscordEntity):
    """
    Sent with a ``Message``, when the it is a response to an ``InteractionEvent``.
    
    Attributes
    ----------
    id : `int`
        The interaction's identifier.
    name : `str`
        The invoked interaction's name.
    type : ``InteractionType``
        The interaction's type.
    user : ``ClientUserBase``
        Who invoked the interaction.
    """
    __slots__ = ('name', 'type', 'user')
    
    def __new__(cls, data, guild_id):
        """
        Creates a new ``MessageInteraction`` from the received data.
        
        Parameters
        ----------
        data : `dict` of (`str`, `Any`) items
            Message interaction data.
        guild_id : `int`
            The respective message's guild's identifier.
        """
        self = object.__new__(cls)
        self.id = int(data['id'])
        self.name = data['name']
        self.type = InteractionType.get(data['type'])
        self.user = User.from_data(data['user'], data.get('member', None), guild_id)
        
        return self
    
    
    def __repr__(self):
        """Returns the message interaction's representation."""
        repr_parts = ['<', self.__class__.__name__, ' id=', repr(self.id), ', type=']
        
        interaction_type = self.type
        repr_parts.append(interaction_type.name)
        repr_parts.append(' (')
        repr_parts.append(repr(interaction_type.value))
        repr_parts.append(')')
        
        repr_parts.append(', name=')
        repr_parts.append(repr(self.name))
        repr_parts.append('>')
        
        return ''.join(repr_parts)
    
    
    def to_data(self):
        """
        Tries to convert the message interaction back to json serializable dictionary.
        
        Returns
        -------
        data : `dict` of (`str`, `Any`)
        """
        return {
            'id': str(self.id),
            'name': str(self.name),
            'type': self.type.value,
            'user': self.user.to_data()
        }
