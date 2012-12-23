from django.db import models
from Outputs.BaseOutputModels import BaseOutputModel,BaseMomendsDataModel


class AnimationMomendData(BaseMomendsDataModel):
    pass

class AnimationData(BaseOutputModel):
    momend = models.ForeignKey(AnimationMomendData)
    pass
