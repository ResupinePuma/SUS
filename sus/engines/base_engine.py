from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Publication():
    title : str
    content: str
    publishedDate : datetime
    url : str
    media : list

class Parser(ABC):
    @abstractmethod 
    def __init__(self):
        pass

    @abstractmethod 
    def Prepare_url(self, url : str, **kwargs):
        """
        Checks if url belogs to reddit domain

        Parameters
        ----------
        url : str
            Url of source

        Returns
        -------
        tuple
            url, url for parsing 
        """
        return str(), str()

    @abstractmethod 
    def GetTitle(self, element : object, **kwargs):
        """
        Extracts title from represented object if it exist. Else gets first sentence from text or first 10 word of text.

        Parameters
        ----------
        element : object
            Etree object

        Returns
        -------
        str
            text of title 
        """
        return str()

    @abstractmethod 
    def GetContent(self, element : object, **kwargs):
        """
        Extracts content from represented object if it exist.

        Parameters
        ----------
        element : object
            Etree object

        Returns
        -------
        str
            text of content 
        """
        return str()

    @abstractmethod 
    def GetPublishedDate(self, element : object, **kwargs):
        """
        Extracts datetime object from time string in represented object if it exist.

        Parameters
        ----------
        element : object
            Etree object

        Returns
        -------
        datetime.datetime
        """
        return datetime()

    @abstractmethod 
    def GetURL(self,element : object, **kwargs):
        """
        Extracts url from time string in represented object if it exist.

        Parameters
        ----------
        element : object
            Etree list of objects

        Returns
        -------
        str
            extracted url
        """
        return str()

    @abstractmethod 
    def GetMedia(self, element : object, **kwargs):
        """
        Not implemented yet
        """
        return list(str)

    @abstractmethod
    def ParseOne(self, url : str, **kwargs):
        """
        Parses one element from list of publications

        Parameters
        ----------
        one_publication : object
            Etree list of objects

        Returns
        -------
        str
            id of post

        Publication
            Publication dataclass
        """
        return Publication()

    @abstractmethod 
    def Parse(self, url, **kwargs):
        """
        Extracts content from represented object if it exist.

        Parameters
        ----------
        url : str
            url of resource

        Returns
        -------
        list
            list of publication dataclasses 
        """
        return list(Publication)

class BadUrlException(Exception):
    pass