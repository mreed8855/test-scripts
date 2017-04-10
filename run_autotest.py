#!/usr/bin/python3.5
"""
This example:

1. Connects to current model and resets it.
2. Deploys an autotest  unit.
3. Clones a custom client test repo which is set using a juju config option
4. Runs an action against autotest, which is a custom action that runs
   three test cases called sleeptest sleeptest1 and sleeptest2
4. Waits for the action results to come back, then exits.

"""
import asyncio
import logging

from juju import loop
from juju.model import Model

MB = 1
Testnames = ['sleeptest', 'sleeptest1', 'sleeptest2']

async def run_action(unit, test_name):
    logging.debug('Running action on unit %s', unit.name)

    # unit.run() returns a juju.action.Action instance
    action = await unit.run_action('custom', testnames=test_name)
    # wait for the action to complete
    action = await action.wait()

    logging.debug("Action results: %s", action.results)


async def main():
    model = Model()
    await model.connect_current()
    await model.reset(force=True)


    autotest_app = await model.deploy(
        '/home/ubuntu/charms/autotest/trusty/autotest',
        application_name='autotest',
        series='trusty',
#        channel='stable',
    )

    await autotest_app.set_config({'autotest-custom-tests': 'https://github.com/mreed8855/custom-tests.git'})

    for tests in Testnames:
        for unit in autotest_app.units:
            await run_action(unit, tests)

    await model.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    loop.run(main())
