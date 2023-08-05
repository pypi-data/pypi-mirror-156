import json
import inspect
import sagemaker_utils
from time import gmtime, strftime
from sagemaker.estimator import Estimator
from sagemakerify import utils, globals, handler

class TrainingJob():
    def __init__(self, function, **kwargs):

        self.session = kwargs.get('session', globals.DEFAULTS.get('session', None))
        
        self.default_prefix = globals.DEFAULTS.get('prefix', 'sagemakerify')
        self.default_bucket = globals.DEFAULTS.get('bucket',  self.session.default_bucket())

        self.base_image = kwargs.get('base_image', globals.DEFAULTS.get('base_image', None))
        self.secret = kwargs.get('secret', globals.DEFAULTS.get('secret', None))
        self.codebuild_role = kwargs.get('codebuild_role', globals.DEFAULTS.get('codebuild_role', None))
        self.instance_count = kwargs.get('instance_count', globals.DEFAULTS.get('instance_count', None))
        self.instance_type = kwargs.get('instance_type', globals.DEFAULTS.get('instance_type', None))
        self.role = kwargs.get('role', globals.DEFAULTS.get('role', None))
        self.volume_size_in_gb = kwargs.get('volume_size_in_gb', globals.DEFAULTS.get('volume_size_in_gb', None))
        self.max_runtime_in_seconds = kwargs.get('max_runtime_in_seconds', globals.DEFAULTS.get('max_runtime_in_seconds', None))
        self.base_job_name = kwargs.get('base_job_name', f"{self.default_prefix}").lower()
        self.image_env = kwargs.get('image_env', {})    
        self.data_s3_prefix = kwargs.get('data_s3_prefix', None)
        self.model_s3_prefix = kwargs.get('model_s3_prefix', None)
        self.code_s3_prefix = kwargs.get('code_s3_prefix', None)
        self.image_s3_prefix = kwargs.get('image_s3_prefix', None)
        self.image_uri = kwargs.get('image_uri', None)
        self.libraries = kwargs.get('libraries', None)
        self.dependencies = kwargs.get('dependencies', None)
        self.image_name = kwargs.get('image_name', None)
        self.others = kwargs.get('others', None)
        self.metrics = kwargs.get('metrics', None)

        build_image = self.image_uri is None

        self.role = utils.get_execution_role(self.role)

        if self.instance_count is None or self.instance_count <= 0:
            raise Exception('instance_count is required and must be grather than 0')
        elif self.instance_type is None:
            raise Exception('instance_type is required')
        elif self.role is None:
            raise Exception('role is required')
        elif self.volume_size_in_gb is None or self.volume_size_in_gb <5:
            raise Exception('volume_size_in_gb is required and must be grather or equal to 5 GB')
        elif self.max_runtime_in_seconds is None or self.max_runtime_in_seconds <= 0:
            raise Exception('max_runtime_in_seconds is required and must be grather than 0')
        
        if build_image:
            #Create docker image
            if self.base_image is None:
                raise Exception('base_image is required')
            elif self.codebuild_role is None:
                raise Exception('codebuild_role is required or set it globally')
            
            if self.image_s3_prefix is None or len(self.image_s3_prefix)==0:            
                self.image_s3_prefix = f's3://{self.default_bucket}/{self.default_prefix}/docker_images'

        if self.code_s3_prefix is None:
            self.code_s3_prefix = f's3://{self.default_bucket}/{self.default_prefix}/code'

        if self.data_s3_prefix is None:
            self.data_s3_prefix = f's3://{self.default_bucket}/{self.default_prefix}/data'

        if self.model_s3_prefix is None:
            self.model_s3_prefix = f's3://{self.default_bucket}/{self.default_prefix}/models'

        # Create a file with the code received
        self.function_name, self.function_file = utils.create_function_file(function)

        # Create handler code
        handler_file = f'{globals.DEFAULTS.source_code_location}/handler.py'        
        sagemaker_utils.make_dirs(handler_file)        
        with open(handler_file, 'w') as f:
            f.write(inspect.getsource(handler))

        self.prefix_job_name = f'{self.base_job_name}-{self.function_name}'.lower().replace('_','-')

        if build_image:
            #Create docker image                        
            self.parameters = {
                'image_name': self.image_name if self.image_name is not None else self.prefix_job_name,
                'base_image': self.base_image,
                's3_path': self.image_s3_prefix,
                'role': self.codebuild_role,
                'wait': True}

            if self.libraries is not None:
                self.parameters['libraries'] = self.libraries
            else:
                self.parameters['libraries'] = []

            self.parameters['libraries']['sagemaker-training'] = '3.9.2'
            
            if self.secret is not None:
                self.parameters['secret'] = self.secret

            if self.dependencies is not None:
                self.parameters['dependencies'] = self.dependencies
            else:
                self.parameters['dependencies'] = []

            self.parameters['dependencies'].append((handler_file,'/opt/ml/code/handler.py'))

            if self.others is not None:
                self.parameters['others'] = self.others
                                
                    
            self.parameters['env'] = self.image_env
            self.parameters['env']['SAGEMAKER_SUBMIT_DIRECTORY'] = '/opt/ml/code'
            self.parameters['env']['SAGEMAKER_PROGRAM'] = 'handler.py'

            hash = utils.dict_hash(self.parameters)
            if self.parameters['image_name'] not in globals.LAST_CONFIG \
                or (self.parameters['image_name'] in globals.LAST_CONFIG \
                    and globals.LAST_CONFIG[self.parameters['image_name']]['hash'] != hash):
                
                self.image_uri = sagemaker_utils.create_docker_image(**self.parameters)       
                
                globals.LAST_CONFIG[self.parameters['image_name']]={
                    'uri': self.image_uri,
                    'hash': hash
                }
            else:
                self.image_uri = globals.LAST_CONFIG[self.parameters['image_name']]['uri']                

    def __call__(self, *args, **kwargs):
        job_name = f'{self.prefix_job_name}-{strftime("%H-%M-%S", gmtime())}'.lower()

        # Set arguments                 
        arguments_types = {'__arguments_data_types__':True}
        arguments = []
        for k in kwargs:
            if utils.is_builtin_class_instance(kwargs[k]):                         
                arguments_types[k] = type(kwargs[k])
                arguments.append(f"--{k.replace('_','-')}")
                if arguments_types[k] is dict:
                    arguments.append(json.dumps(kwargs[k]))
                else:                    
                    arguments.append(str(kwargs[k]))
            else:
                raise Exception(f'{type(kwargs[k])} is not supported')   
        
        if len(arguments)>0:
            args = args + (arguments_types,)

        # Serialize data
        data_file = utils.to_pkl(args,f'{globals.DEFAULTS.source_code_location}/data.pkl')

        # Upload function code to S3        
        function_s3_path = sagemaker_utils.upload(self.function_file, f'{self.code_s3_prefix}/{job_name}', session = self.session.boto_session)

        # Upload data to S3            
        data_s3_path = sagemaker_utils.upload(data_file, f'{self.data_s3_prefix}/{job_name}', session = self.session.boto_session)

        arguments.append('--module')
        arguments.append(self.function_name)

        print(f"arguments: {arguments}")
        
        # Creates a SageMaker Estimator
        parameteres = {
            'image_uri': self.image_uri,
            'entrypoint': 'handler.py',            
            'role': self.role,
            'instance_count': self.instance_count,
            'instance_type': self.instance_type,            
            'output_path': f'{self.model_s3_prefix}/{job_name}',                        
            'volume_size': self.volume_size_in_gb,
            'max_run': self.max_runtime_in_seconds,
            'hyperparameters': {arguments[i].replace('--',''): arguments[i+1] for i in range(0, len(arguments)-1, 2)},
            'sagemaker_session': self.session
        }

        if(self.metrics is not None):
            parameteres['metric_definitions'] = self.metrics

        self.estimator = Estimator(**parameteres)        

        self.estimator.fit({'data':data_s3_path, 'code':function_s3_path})

        self.model_data = self.estimator.latest_training_job.describe()['ModelArtifacts']['S3ModelArtifacts']

        return sagemaker_utils.read_pkl(self.model_data, session = self.session.boto_session)     

def sm_training_job(**kwargs):
    def wrapper(function):
        return TrainingJob(function, **kwargs)
    
    return wrapper