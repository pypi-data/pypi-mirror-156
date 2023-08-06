import os
from dataclasses import dataclass
from optuna.distributions import LogUniformDistribution, UniformDistribution

class Loggers:
    WANDB = "wandb"
    STREAMLIT = "streamlit"

@dataclass
class BaseLogger:
    pass

@dataclass
class WandbConfig(BaseLogger):

    @staticmethod
    def validate():
        if os.getenv("WANDB_ENTITY") is None:
            raise Exception("Please, use lightning run app ... --env WANDB_API_KEY=X")
        if os.getenv("WANDB_API_KEY") is None:
            raise Exception("Please, use lightning run app ... --env WANDB_API_KEY=X")

    @classmethod
    def get_sweep_config(cls, distributions):

        parameters = {}
        for k, d in distributions.items():
            parameters[k] = {}
            distribution_name = cls._to_distribution_name(d)
            if distribution_name:
                parameters[k]['distribution'] = distribution_name
            parameters[k].update(cls._to_distribution_values(d))

        sweep_config = {
            'method': 'random',
            'metric': {
                'name': 'loss',
                'goal': 'minimize'
            },
            'parameters': parameters
        }

        return sweep_config

    @staticmethod
    def _to_distribution_name(d):
        if isinstance(d, LogUniformDistribution):
            return "q_log_uniform_values"
        elif isinstance(d, UniformDistribution):
            return "uniform"
        return

    @staticmethod
    def _to_distribution_values(d):
        if isinstance(d, (LogUniformDistribution, UniformDistribution)):
            return {"min": d.low, "max": d.high}
        return [v for v in d.choices]