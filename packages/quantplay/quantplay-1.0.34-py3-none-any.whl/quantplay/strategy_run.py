from quantplay.strategies.options.intraday.musk import Musk
from quantplay.executor.strategy_executor import UserStrategiesExecutor
strategies = [Musk()]

UserStrategiesExecutor("Zerodha", strategies).start_execution()