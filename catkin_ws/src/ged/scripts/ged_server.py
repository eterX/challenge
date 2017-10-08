#! /usr/bin/env python
#
# entry point for the Ged client
#
# author: Leandro Batlle
#
#
#std
import sys,math,time

#ROS
import rospy
from turtlesim.msg import Pose

#Ged
import ACBged as acbg #Ged's own package, svr and cnt stuff




if __name__ == '__main__XXXXXXXXXXX':
    try:
        # Initializes a rospy node so that the SimpleActionClient can
        # publish and subscribe over ROS.
        rospy.init_node('ged_client_py')
        result = acbg.prueba()
        print("Result: {}".format(result))
    except rospy.ROSInterruptException:
        #print("program interrupted before completion", file=sys.stderr)
        print("program interrupted before completion", sys.stderr)




import rospy

import actionlib
import actionlib_tutorials.msg
import geometry_msgs.msg as geomsg
import ged.msg as gmsg
import std_msgs.msg as smsg

class gedAction(object):
    # create messages that are used to publish feedback/result
    # _feedback = actionlib_tutorials.msg.FibonacciFeedback()
    # _result = actionlib_tutorials.msg.FibonacciResult()
    
    #_feedback = gmsg.goToPointPolarActionFeedback()
    #_result = gmsg.goToPointPolarActionResult() #has header and goalid
    _feedback = gmsg.goToPointPolarFeedback()
    _result = gmsg.goToPointPolarResult()

    def __init__(self, name):
        self._action_name = name
        self.pose = Pose()
        #self._as = actionlib.SimpleActionServer(self._action_name, actionlib_tutorials.msg.FibonacciAction, execute_cb=self.execute_cb, auto_start = False)
        self._as = actionlib.SimpleActionServer(self._action_name, gmsg.goToPointPolarAction, execute_cb=self.execute_cb,  auto_start = False)
        self._as.start() #do not replace with auto_start...


        self.pubtwist = rospy.Publisher('/ged/turtle1/cmd_vel', geomsg.Twist, queue_size=10)
        self.pubWeb= rospy.Publisher('/ged/listener', smsg.String, queue_size=10)


    def pose_callback(self, data):
        print("pose_callback")
        self.pose = data
        self.pose.x = round(self.pose.x, 4)
        self.pose.y = round(self.pose.y, 4)
        self._feedback.xfeed=self.pose.x
        self._feedback.yfeed=self.pose.y
        pubWebMsg=smsg.String()
        pubWebMsg.data="micursor.move({},{})".format(self.pose.x,self.pose.y)
        self.pubWeb.publish(pubWebMsg)
        self._as.publish_feedback(self._feedback) #keep the client in the loop




    def execute_cb(self, goal):
        # helper variables
        r = rospy.Rate(5)
        success = True
        #Callback function implementing the pose value received

        # publish info to the console for the user
        rospy.loginfo('%s: Executing, ' % (self._action_name))


        # start executing the action
        # check that preempt has not been requested by the client
        if self._as.is_preempt_requested():
            rospy.loginfo('%s: server is Preempted' % self._action_name)
            self._as.set_preempted()
            success = False
            #self._feedback.sequence = ["Preempted",]
            #self._feedback.sequence = actionlib.GoalStatus.PREEMPTED
        else:
            #miwist=geomsg.Twist(linear=geomsg.Vector3(x=goal.len),angular=geomsg.Vector3(x=goal.ang))
            if goal.ang != 0:
                miwist=geomsg.Twist(angular=geomsg.Vector3(z=-goal.ang*2*math.pi/360)) #to rad CW
                self.pubtwist.publish(miwist,)

            if goal.len != 0:
                miwist=geomsg.Twist(linear=geomsg.Vector3(x=goal.len))
                self.pose_subscriber = rospy.Subscriber('/ged/turtle1/pose', Pose, self.pose_callback)
                self.pubtwist.publish(miwist)
                r.sleep()
                self.pose_subscriber.unregister()
                #                self.pubtwist.publish(miwist)
                #                    self._as.publish_feedback(self._feedback)
                #                    r.sleep()


                #self._feedback.status = actionlib.GoalStatus.SUCCEEDED #no need, state is a member or result
                # this step is not necessary, the sequence is computed at 1 Hz for demonstration purposes
                #        r.sleep()

        if success:
            #self._result.result(x=1,y=2)
            #self._result.sequence = self._feedback.sequence
            rospy.loginfo('%s: Succeeded' % self._action_name)
            #self._as.set_succeeded(self._result)

if __name__ == '__main__':
    rospy.init_node('ged_server_py',)
    server = gedAction(rospy.get_name())
    rospy.spin()
