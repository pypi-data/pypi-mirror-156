from copy import deepcopy
import jsonpickle
try:
    from argo.workflows.client import (
        V1alpha1WorkflowStep,
        V1alpha1Arguments,
        V1VolumeMount,
        V1alpha1ContinueOn,
        V1alpha1ResourceTemplate
    )
    from .client import V1alpha1Sequence
except:
    pass
from .common import S3Artifact
from .io import InputArtifact, InputParameter, OutputArtifact, OutputParameter, PVC, ArgoVar
from .op_template import ShellOPTemplate, PythonScriptOPTemplate
from .util_ops import CheckNumSuccess, CheckSuccessRatio

def argo_range(*args):
    """
    Return a str representing a range of integer in Argo
    It receives 1-3 arguments, which is similar to the function `range` in Python
    Each argument can be Argo parameter
    """
    start = 0
    step = 1
    if len(args) == 1:
        end = args[0]
    elif len(args) == 2:
        start = args[0]
        end = args[1]
    elif len(args) == 3:
        start = args[0]
        end = args[1]
        step = args[2]
    else:
        raise TypeError("Expected 1-3 arguments, got %s" % len(args))
    if isinstance(start, (InputParameter, OutputParameter)):
        start = "sprig.atoi(%s)" % start.expr
    if isinstance(step, (InputParameter, OutputParameter)):
        step = "sprig.atoi(%s)" % step.expr
    if isinstance(end, (InputParameter, OutputParameter)):
        end = "sprig.atoi(%s)" % end.expr
    return ArgoVar("toJson(sprig.untilStep(%s, %s, %s))" % (start, end, step))

def argo_sequence(count=None, start=None, end=None, format=None):
    """
    Return a numeric sequence in Argo

    Args:
        count: length of the sequence, can be an Argo parameter
        start: start number of the sequence, can be an Argo parameter
        end: end number of the sequence, can be an Argo parameter
        format: output the sequence with format
    """
    if isinstance(count, ArgoVar):
        count = "{{=%s}}" % count.expr
    if isinstance(start, ArgoVar):
        start = "{{=%s}}" % start.expr
    if isinstance(end, ArgoVar):
        end = "{{=%s}}" % end.expr
    return V1alpha1Sequence(count=count, start=start, end=end, format=format)

def argo_len(param):
    """
    Return the length of a list which is an Argo parameter

    Args:
        param: the Argo parameter which is a list
    """
    return ArgoVar("len(sprig.fromJson(%s))" % param.expr)

class Step:
    """
    Step

    Args:
        name: the name of the step
        template: OP template the step uses
        parameters: input parameters passed to the step as arguments
        artifacts: input artifacts passed to the step as arguments
        when: conditional step if the condition is satisfied
        with_param: generate parallel steps with respect to a list as a parameter
        continue_on_failed: continue if the step fails
        continue_on_num_success: continue if the success number of the generated parallel steps greater than certain number
        continue_on_success_ratio: continue if the success ratio of the generated parallel steps greater than certain number
        with_sequence: generate parallel steps with respect to a sequence
        key: the key of the step
        executor: define the executor to execute the script
        use_resource: use k8s resource
    """
    def __init__(self, name, template, parameters=None, artifacts=None, when=None, with_param=None, continue_on_failed=False,
            continue_on_num_success=None, continue_on_success_ratio=None, with_sequence=None, key=None, executor=None,
            use_resource=None, util_image="alpine:latest"):
        self.name = name
        self.id = self.name
        self.template = template
        self.inputs = deepcopy(self.template.inputs)
        self.outputs = deepcopy(self.template.outputs)
        self.inputs.set_step(self)
        self.outputs.set_step(self)
        self.continue_on_failed = continue_on_failed
        self.continue_on_num_success = continue_on_num_success
        self.continue_on_success_ratio = continue_on_success_ratio
        self.check_step = None
        self.prepare_step = None

        if parameters is not None:
            self.set_parameters(parameters)

        if artifacts is not None:
            self.set_artifacts(artifacts)

        self.when = when
        self.with_param = with_param
        self.with_sequence = with_sequence
        self.key = key
        self.executor = executor
        self.use_resource = use_resource
        self.util_image = util_image

        if self.key is not None:
            self.template.inputs.parameters["dflow_key"] = InputParameter(value="")
            self.inputs.parameters["dflow_key"] = InputParameter(value=str(self.key))

        if hasattr(self.template, "slices") and self.template.slices is not None and self.template.slices.output_artifact is not None:
            new_template = deepcopy(self.template)
            new_template.name = self.template.name + "-" + self.name
            script = ""
            for name in new_template.slices.output_artifact:
                script += "mkdir -p /tmp/outputs/artifacts/%s\n" % name
                script += "echo '{\"path_list\": []}' > /tmp/outputs/artifacts/%s/.dflow.init\n" % name
            init_template = ShellOPTemplate(name="%s-init-artifact" % new_template.name, image=self.util_image,
                image_pull_policy=new_template.image_pull_policy, script=script)
            if self.key is not None:
                new_template.inputs.parameters["dflow_group_key"] = InputParameter(value="")
                self.inputs.parameters["dflow_group_key"] = InputParameter(value=str(self.key).replace("{{item}}", "group"))
                init_template.inputs.parameters["dflow_group_key"] = InputParameter()
                for name in new_template.slices.output_artifact:
                    init_template.outputs.artifacts[name] = OutputArtifact(path="/tmp/outputs/artifacts/%s" % name,
                        save=S3Artifact(key="{{workflow.name}}/{{inputs.parameters.dflow_group_key}}/%s" % name), archive=None)
                    new_template.outputs.artifacts[name].save.append(S3Artifact(
                        key="{{workflow.name}}/{{inputs.parameters.dflow_group_key}}/%s" % name))
                self.prepare_step = Step(name="%s-init-artifact" % self.name, template=init_template,
                    parameters={"dflow_group_key": str(self.key).replace("{{item}}", "group")})
            else:
                init_template.outputs.parameters["dflow_artifact_key"] = OutputParameter(value="{{workflow.name}}/{{pod.name}}")
                new_template.inputs.parameters["dflow_artifact_key"] = InputParameter(value="")
                self.inputs.parameters["dflow_artifact_key"] = InputParameter(value="{{steps.%s-init-artifact.outputs.parameters.dflow_artifact_key}}" % self.name)
                for name in new_template.slices.output_artifact:
                    init_template.outputs.artifacts[name] = OutputArtifact(path="/tmp/outputs/artifacts/%s" % name,
                        save=S3Artifact(key="{{workflow.name}}/{{pod.name}}/%s" % name), archive=None)
                    new_template.outputs.artifacts[name].save.append(S3Artifact(
                        key="{{inputs.parameters.dflow_artifact_key}}/%s" % name))
                self.prepare_step = Step(name="%s-init-artifact" % self.name, template=init_template)
            for name in new_template.slices.output_artifact:
                self.outputs.artifacts[name].redirect = self.prepare_step.outputs.artifacts[name]
            self.template = new_template

    def __repr__(self):
        return self.id

    def set_parameters(self, parameters):
        for k, v in parameters.items():
            # if a parameter is saved as artifact, the parameters it pass value to or its value comes from must be saved as artifact as well
            if isinstance(v, (InputParameter, OutputParameter)):
                if self.inputs.parameters[k].type is None and v.type is not None:
                    self.inputs.parameters[k].type = v.type
                if v.type is None and self.inputs.parameters[k].type is not None:
                    v.type = self.inputs.parameters[k].type

                if self.inputs.parameters[k].save_as_artifact:
                    v.save_as_artifact = True
                if v.save_as_artifact:
                    self.inputs.parameters[k].save_as_artifact = True

            if self.inputs.parameters[k].save_as_artifact and isinstance(v, (InputParameter, OutputParameter, InputArtifact, OutputArtifact)):
                self.inputs.parameters[k].source = v
                return

            if v is None:
                self.inputs.parameters[k].value = "null"
            else:
                self.inputs.parameters[k].value = v

    def set_artifacts(self, artifacts):
        for k, v in artifacts.items():
            if v is None:
                del self.inputs.artifacts[k]
                self.template.inputs.artifacts[k].optional = True
            else:
                self.inputs.artifacts[k].source = v

    def convert_to_argo(self, context=None):
        argo_parameters = []
        argo_artifacts = []
        for par in self.inputs.parameters.values():
            if par.save_as_artifact:
                argo_artifacts.append(par.convert_to_argo())
            else:
                argo_parameters.append(par.convert_to_argo())

        new_template = None

        pvc_arts = []
        for art in self.inputs.artifacts.values():
            if isinstance(art.source, PVC):
                pvc_arts.append((art.source, art))
            elif art.source is None and art.optional == True:
                pass
            else:
                argo_artifacts.append(art.convert_to_argo())

        if len(pvc_arts) > 0:
            if new_template is None:
                new_template = deepcopy(self.template)
                new_template.name = self.template.name + "-" + self.name
            if (isinstance(new_template, ShellOPTemplate)):
                for pvc, art in pvc_arts:
                    del new_template.inputs.artifacts[art.name]
                    new_template.script = "ln -s /tmp/mnt/%s %s\n" % (pvc.subpath, art.path) + new_template.script
                    new_template.mounts.append(V1VolumeMount(name=pvc.name, mount_path="/tmp/mnt"))
                    new_template.pvcs.append(pvc)
            elif (isinstance(new_template, PythonScriptOPTemplate)):
                for pvc, art in pvc_arts:
                    del new_template.inputs.artifacts[art.name]
                    new_template.script = "os.system('ln -s /tmp/mnt/%s %s')\n" % (pvc.subpath, art.path) + new_template.script
                    new_template.mounts.append(V1VolumeMount(name=pvc.name, mount_path="/tmp/mnt"))
                    new_template.pvcs.append(pvc)
                new_template.script = "import os\n" + new_template.script
            else:
                raise RuntimeError("Unsupported type of OPTemplate to mount PVC")
        
        pvc_arts = []
        for art in self.outputs.artifacts.values():
            for save in art.save:
                if isinstance(save, PVC):
                    pvc_arts.append((save, art))

        if len(pvc_arts) > 0:
            if new_template is None:
                new_template = deepcopy(self.template)
                new_template.name = self.template.name + "-" + self.name
            if (isinstance(new_template, ShellOPTemplate)):
                new_template.script += "\n"
                for pvc, art in pvc_arts:
                    new_template.mounts.append(V1VolumeMount(name=pvc.name, mount_path="/tmp/mnt"))
                    new_template.script += "cp -r %s /tmp/mnt/%s\n" % (art.path, pvc.subpath)
                    new_template.pvcs.append(pvc)
            elif (isinstance(new_template, PythonScriptOPTemplate)):
                new_template.script += "\nimport os\n"
                for pvc, art in pvc_arts:
                    new_template.mounts.append(V1VolumeMount(name=pvc.name, mount_path="/tmp/mnt"))
                    new_template.script += "os.system('cp -r %s /tmp/mnt/%s')\n" % (art.path, pvc.subpath)
                    new_template.pvcs.append(pvc)
            else:
                raise RuntimeError("Unsupported type of OPTemplate to mount PVC")

        if self.continue_on_num_success or self.continue_on_success_ratio is not None:
            self.continue_on_failed = True
            if new_template is None:
                new_template = deepcopy(self.template)
                new_template.name = self.template.name + "-" + self.name
            if (isinstance(new_template, ShellOPTemplate)):
                new_template.outputs.parameters["dflow_success_tag"] = OutputParameter(value_from_path="/tmp/success_tag", default="0")
                new_template.script += "\n"
                new_template.script += "echo 1 > /tmp/success_tag\n"
            elif (isinstance(new_template, PythonScriptOPTemplate)):
                new_template.outputs.parameters["dflow_success_tag"] = OutputParameter(value_from_path="/tmp/success_tag", default="0")
                new_template.script += "\n"
                new_template.script += "with open('/tmp/success_tag', 'w') as f:\n    f.write('1')\n"
            else:
                raise RuntimeError("Unsupported type of OPTemplate for continue_on_num_success or continue_on_success_ratio")

        if new_template is not None:
            self.template = new_template
            self.outputs = deepcopy(self.template.outputs)
            self.outputs.set_step(self)

        if self.continue_on_num_success is not None:
            self.check_step = Step(
                name="%s-check-num-success" % self.name, template=CheckNumSuccess(image=self.util_image),
                parameters={
                    "success": self.outputs.parameters["dflow_success_tag"],
                    "threshold": self.continue_on_num_success
                }
            )
        elif self.continue_on_success_ratio is not None:
            self.check_step = Step(
                name="%s-check-success-ratio" % self.name, template=CheckSuccessRatio(image=self.util_image),
                parameters={
                    "success": self.outputs.parameters["dflow_success_tag"],
                    "threshold": self.continue_on_success_ratio
                }
            )

        if isinstance(self.with_param, ArgoVar):
            self.with_param = "{{=%s}}" % self.with_param.expr
        elif self.with_param is not None and not isinstance(self.with_param, str):
            self.with_param = jsonpickle.dumps(list(self.with_param))

        if context is not None:
            self.template = context.render(self.template)

        if self.executor is not None:
            self.template = self.executor.render(self.template)

        if self.use_resource is not None:
            self.template.resource = V1alpha1ResourceTemplate(action=self.use_resource.action,
                success_condition=self.use_resource.success_condition, failure_condition=self.use_resource.failure_condition,
                manifest=self.use_resource.get_manifest(self.template.command, self.template.script))

        return V1alpha1WorkflowStep(
            name=self.name, template=self.template.name, arguments=V1alpha1Arguments(
                parameters=argo_parameters,
                artifacts=argo_artifacts
            ), when=self.when, with_param=self.with_param, with_sequence=self.with_sequence,
            continue_on=V1alpha1ContinueOn(failed=self.continue_on_failed)
        )
