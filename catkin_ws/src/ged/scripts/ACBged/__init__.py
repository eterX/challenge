#! /usr/bin/env python

"""
Ged module
"""

#from actionlib_msgs.msg import GoalID, GoalStatus, GoalStatusArray
#rom actionlib.exceptions import ActionException
#stdlibs
from __future__ import print_function
import sys,pickle,json

#ROS
import rospy, actionlib, roslib
#Ged
roslib.load_manifest('ged')
import ged.msg as gmsg

__all__=["segment","mission"]

def prueba():
    import turtle_actionlib.msg as tam

    client = actionlib.SimpleActionClient('ged/shape_server', tam.ShapeAction)
    client.wait_for_server()

    goal = tam.ShapeGoal(edges=3,radius=1)
    # Fill in the goal here
    #goal = actionlib_tutorials.msg.FibonacciGoal(order=20)

    client.send_goal(goal)
    client.wait_for_result(rospy.Duration.from_sec(5.0))
    return client.get_result()

#class segment(object,gmsg.goToPointPolarGoal): #python2 :(
class segment(object): #python2 :(
    """
    atomic component of a mission's path
    as per Requirement 1-I-a
    (milestone %"1.I.a - Go from the current point to any other goal point in 2D space")

    """
    pass

class mission(object): #python2 :(
    """
    a mission takes Robot for the current point in 2D to another, through a 2D path.
    as per Requirement 1-I: "Robot shall perform missions specified by Operator:"
    """
    def __init__(self,designation):
        self._path=list()
        self.designation=designation

    def load(self,pathfile):
        import pickle
        try:
            mifile=open(pathfile,"rb")
            self._path=pickle.load(mifile)
            mifile.close()
        except Exception as e:
            print(e)


    @property
    def path(self):
        return self._path

    @path.setter
    def path(self):
        raise TypeError("path is meant to be a private member. use processPath as setter")

    def processPath(self,path_as_json_string):
        try:
            self._path=json.loads(path_as_json_string)
        except Exception as e:
            rospy.logerr("mission {} path not loaded ".format(self.designation))





if __name__ == '__main__':
    print("ROS package Ged. library, not meant to be run directly")