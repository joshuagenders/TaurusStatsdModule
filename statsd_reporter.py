from bzt.engine import Reporter, Singletone
from bzt.modules.aggregator import DataPoint, AggregatorListener, ResultsProvider
import statsd, os, json

class StatsdReporter(Reporter, AggregatorListener, Singletone):
    def __init__(self):
        self.serialiser = DataSerialiser()
        self.data_buffer = []

    def aggregated_second(self, data):
        self.data_buffer += data

    def prepare(self):
        super(StatsdReporter, self).prepare()

    def check(self):
        for point in self.data_buffer:
            self.serialiser.serialise(point)           
        self.data_buffer = []

    def startup(self):
        super(StatsdReporter, self).startup()

    def shutdown(self):
        super(StatsdReporter, self).shutdown()

class DataSerialiser():
    def __init__(self):
        host = os.getenv("STATSD_HOST", "localhost")
        port = int(os.getenv("STATSD_PORT", "8125"))
        self.client = statsd.StatsClient(host, port)

    def serialise(self, datapoint):
        # todo parse and push datapoints
        output = json.dumps(datapoint)
        print(output)
        