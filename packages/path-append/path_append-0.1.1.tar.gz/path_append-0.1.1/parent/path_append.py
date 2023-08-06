from sys import path
from os import getcwd, path as ospath
if path[0].find("sms_pipeline")!=-1:
    p_path = getcwd()
    parent = ospath.dirname(p_path)
    if "sms_pipeline" in parent.replace("\\","/").split("/"):
        parent = parent.replace("sms_pipeline","")
    path.append(parent)