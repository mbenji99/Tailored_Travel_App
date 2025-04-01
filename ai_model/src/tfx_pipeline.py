
from tfx.components import CsvExampleGen, Trainer, Pusher, Transform
from tfx.orchestration.experimental.interactive.interactive_context import InteractiveContext
from tfx.proto import trainer_pb2, pusher_pb2
from data_config import DATA_PATHS

def run_pipeline():
    context = InteractiveContext()
    
    # ExampleGen with preprocessing
    example_gen = CsvExampleGen(input_base=DATA_PATHS['trips'])
    context.run(example_gen)
    
    # Transform component would be added here for feature engineering
    # ... [transform configuration]
    
    # Trainer with updated model architecture
    trainer = Trainer(
        module_file='trainer_module.py',
        examples=example_gen.outputs['examples'],
        train_args=trainer_pb2.TrainArgs(num_steps=500),
        eval_args=trainer_pb2.EvalArgs(num_steps=100)
    )
    context.run(trainer)
    
    # Pusher for model deployment
    pusher = Pusher(
        model=trainer.outputs['model'],
        push_destination=pusher_pb2.PushDestination(
            filesystem=pusher_pb2.PushDestination.Filesystem(
                base_directory='serving_model'
            )
        )
    )
    context.run(pusher)