#! /usr/bin/env python

#stdlibs
from __future__ import print_function
import sys,os
#ROS
import rospy, actionlib

#Ged
import ged.msg as gmsg
import ACBged as acbg


# Brings in the messages used by the fibonacci action, including the
# goal message and the result message.
import actionlib_tutorials.msg

micounter={"done":0,"active":0,"feedback":0}

def ged_client():
    def done_cb(state,result):
        """

        :param state: int from actionlib_msgs/GoalStatus
        :param result:
        :return:
        """
        global micounter
        micounter["done"]+=1
        print("Segment done; {}".format(micounter["done"]))

    def active_cb():
        """
        goal active, do nothing (?)
        :return:
        """
        global micounter
        micounter["active"]+=1
        print("Segment active; {}".format(micounter["active"]))



    def feedback_cb(feedback):
        """

        :param feedback:
        :return:
        """
        global micounter
        micounter["feedback"]+=1
        print("Interim Robot position; x,y = ({},{})".format(feedback.xfeed,feedback.yfeed)) #theta te la debo
        #print("feedback: {}".format(micounter["feedback"]))


    # Creates the SimpleActionClient, passing the type of the action
    #client = actionlib.SimpleActionClient('ged_server_py', actionlib_tutorials.msg.FibonacciAction)
    client = actionlib.SimpleActionClient('ged/ged_server_py', gmsg.goToPointPolarAction)
    #    client = actionlib.SimpleActionClient('ged_server_py', gmsg.goToPointPolarAction)

    # Waits until the action server has started up and started
    # listening for goals.
    client.wait_for_server()

    mymission=acbg.mission()
    try:
        mymission.load(os.path.dirname(os.path.realpath(__file__))+"/test_mission2.pickle") #TODO: proper file storage
    except Exception as e:
        raise  #TODO: validate loaded missions

    if False: #the quest for the goalid and some feedback key
        # Creates a goal to send to the action server.
        #goal = actionlib_tutorials.msg.FibonacciGoal(order=4)
        #goal = gmsg.goToPointPolarGoal(len=1,ang=45)
        #goal.goal_id="mi_goal_id" # should I Send the goalid to the action server.
        if True:
            mysegment=gmsg.goToPointPolarGoal()
            mysegment.len=1.0
        else: # if goToPointPolarActionGoal() is not meant to be sent... where does goal_id come from?
            i=10
            mysegment=gmsg.goToPointPolarActionGoal()
            mysegment.goal_id.id=str(i)
            mysegment.goal.len=1.0
            i+=1
        client.send_goal(mysegment, done_cb=done_cb, active_cb=active_cb, feedback_cb=feedback_cb)
        print(dir(client))


    for mysegment in mymission.path:
        client.send_goal(mysegment, done_cb=done_cb, active_cb=active_cb, feedback_cb=feedback_cb)
        # Waits for the server to finish performing the action.
        client.wait_for_result()

    # Prints out the result of executing the action
    return client.get_result()  # A FibonacciResult

if __name__ == '__main__':
    try:
        # Initializes a rospy node so that the SimpleActionClient can
        # publish and subscribe over ROS.
        rospy.init_node('ged_client_py')
        result = ged_client()
        print("Result: {}".format(result.__repr__))
    except rospy.ROSInterruptException:
        print("program interrupted before completion", file=sys.stderr)