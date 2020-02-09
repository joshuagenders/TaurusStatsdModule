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
        host = os.getenv("STATSD_HOST", "localhost")
        port = int(os.getenv("STATSD_PORT", "8125"))
        prefix = os.getenv("STATSD_PREFIX", "taurus.unset")
        self.client = statsd.StatsClient(host, port, prefix)

    def serialise(self, data):
        cur = data[DataPoint.CURRENT].get('')
        self.client.gauge('concurrency', cur[KPISet.CONCURRENCY])
        self.client.gauge('errors', cur[KPISet.FAILURES])
        self.client.gauge('success', cur[KPISet.SUCCESSES])
        self.client.gauge('total', cur[KPISet.SAMPLE_COUNT])
        self.client.timer('response', cur[KPISet.AVG_RESP_TIME])
        self.client.timer('latency', cur[KPISet.AVG_LATENCY])
        self.client.timer('connect', cur[KPISet.AVG_CONN_TIME])
        self.client.timer('min', cur[KPISet.PERCENTILES]['0.0'])
        self.client.timer('p50', cur[KPISet.PERCENTILES]['50.0'])
        self.client.timer('p90', cur[KPISet.PERCENTILES]['90.0'])
        self.client.timer('p95', cur[KPISet.PERCENTILES]['95.0'])
        self.client.timer('p99', cur[KPISet.PERCENTILES]['99.0'])
        self.client.timer('p999', cur[KPISet.PERCENTILES]['99.9'])
        self.client.timer('max', cur[KPISet.PERCENTILES]['100.0'])