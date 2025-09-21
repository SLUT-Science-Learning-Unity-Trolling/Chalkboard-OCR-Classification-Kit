from punq import Container

from app.infrastructure.gateways.mongo import MongoGateway


def build_container() -> Container:

    container = Container()

    container.register(
        MongoGateway,
        instance=MongoGateway(uri="mongodb://0.0.0.0:27017", db_name="test"),
    )

    return container
