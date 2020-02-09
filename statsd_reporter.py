from bzt.engine import Reporter, Singletone
from bzt.modules.aggregator import DataPoint, KPISet, AggregatorListener, ResultsProvider
import statsd, os

class StatsdReporter(Reporter, AggregatorListener, Singletone):
    def __init__(self):
        super(StatsdReporter, self).__init__()
        self.serialiser = DataSerialiser()
        self.data_buffer = []

    def aggregated_second(self, data):
        self.data_buffer.append(data)

    def prepare(self):
        super(StatsdReporter, self).prepare()
        self.engine.aggregator.add_listener(self)

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
        host = os.getenv("STATSD_HOST", "127.0.0.1")
        port = int(os.getenv("STATSD_PORT", "8125"))
        prefix = os.getenv("STATSD_PREFIX", "taurus.test")
        print("StatsdReporter: %s:%s %s" % (host, port, prefix))
        self.client = statsd.StatsClient(host, port, prefix)

    def serialise(self, data):
        cur = data[DataPoint.CURRENT].get('')
        self.client.gauge('concurrency', cur[KPISet.CONCURRENCY])
        self.client.incr('errors', cur[KPISet.FAILURES])
        self.client.incr('success', cur[KPISet.SUCCESSES])
        self.client.incr('total', cur[KPISet.SAMPLE_COUNT])
        self.client.timing('response', cur[KPISet.AVG_RESP_TIME])
        self.client.timing('latency', cur[KPISet.AVG_LATENCY])
        self.client.timing('connect', cur[KPISet.AVG_CONN_TIME])
        self.client.timing('min', cur[KPISet.PERCENTILES]['0.0'])
        self.client.timing('p50', cur[KPISet.PERCENTILES]['50.0'])
        self.client.timing('p90', cur[KPISet.PERCENTILES]['90.0'])
        self.client.timing('p95', cur[KPISet.PERCENTILES]['95.0'])
        self.client.timing('p99', cur[KPISet.PERCENTILES]['99.0'])
        self.client.timing('p999', cur[KPISet.PERCENTILES]['99.9'])
        self.client.timing('max', cur[KPISet.PERCENTILES]['100.0'])