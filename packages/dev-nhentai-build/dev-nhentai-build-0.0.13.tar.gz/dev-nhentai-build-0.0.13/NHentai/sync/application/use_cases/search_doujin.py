from NHentai.core.propagate import PropagateMessage
from NHentai.sync.infra.adapters.brokers.broker_interface import BrokerInterface
from NHentai.sync.infra.adapters.brokers.implementations.pubsub import PubSubMessage
from NHentai.sync.infra.adapters.repositories.hentai.implementations.nhentai import NhentaiInterface

class SearchDoujinUseCase:
    def __init__(self, 
                 nhentai_repo: NhentaiInterface,
                 message_broker: BrokerInterface[PubSubMessage]):
        self.nhentai_repo = nhentai_repo
        self.message_broker = message_broker
  
    def execute(self, query: str, sort: str='recent', page: int=1):
        result = self.nhentai_repo.search_doujin(search_term=query, sort=sort, page=page)
        PropagateMessage.publish(adapter=self.message_broker, data=result.doujins)
        return result