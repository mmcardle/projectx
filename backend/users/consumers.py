from channels.consumer import SyncConsumer


class usersConsumer(SyncConsumer):

    def app1_message(self, message):
        # do something with message
        pass