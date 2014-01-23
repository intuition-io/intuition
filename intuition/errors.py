#
# Copyright 2014 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class IntuitionError(Exception):
    ''' Base class for exceptions in Intuition module '''
    msg = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.message = str(self)

    def __str__(self):
        msg = self.msg.format(**self.kwargs)
        return msg

    __unicode__ = __str__
    __repr__ = __str__


class ImportContextFailed(IntuitionError):
    msg = "unable to import context builer from {module}: {reason}"


class InvalidConfiguration(IntuitionError):
    msg = "invalid configuration: {config} ({module})"


class PortfolioOptimizationFailed(IntuitionError):
    msg = """
[{date}] \
Portfolio optimization failed: {reason}, \
processing {data}
""".strip()


class AlgorithmEventFailed(IntuitionError):
    msg = """
[{date}] \
algorithm event failed: {reason}, \
processing {data}
""".strip()
