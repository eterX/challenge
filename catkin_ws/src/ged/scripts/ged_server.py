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

monitor_updates = True #TODO: config file
cursors_collection_size = 10
trails_collection_size = 10
cursors_collection=list() #global... 
trails_collection=list()
cursor_move_template="cursor_move({id},{x},{y},{show});"
cursor_rotate_template="cursor_rotate({id},{theta});"
trail_points_template="trail_points({id},{points});"


class cursor(object): #python2
    """
    tracks remote Monitor entities
    """
    #TODO: superclass
    def __init__(self,id):
        self.id=id #TODO: validate natural integer < max 
        self.show=False
        self.trail=trails_collection[id] #defaults to the same trailid as its own

    def move(self,newpose):
        result=list()
        x=newpose.x
        y=newpose.y
        theta=newpose.theta
        if self.show:
            show="true"
        else:
            show="false"
        self.trail.appendpoint(x,y)
        result.append(cursor_move_template.format(id=str(self.id),
                                                  x=str(int(x*1000/11)), #TODO: send this to a "representation layer"
                                                  y=str(int(1000*(1-y/11))),
                                                  show=show))
        result.append(cursor_rotate_template.format(id=str(self.id),theta=int(-theta*360/2/math.pi)))
        result.append(trail_points_template.format(id=str(self.id),points=self.trail.points))



        return result


class trail(object): #python2
    """
    tracks remote Monitor entities
    """
    def __init__(self,id):
        self.id=id #TODO: validate natural integer < max
        self.__points=list()
        #self.points=""  #string SVG.poligon.piints format

    @property
    def points(self): #getter
        result=""
        for point in self.__points:
            result+=" "+str(int(point[0]*1000/11)) #TODO: send this to a "representation layer"
            result+=" "+str(int(1000*(1-point[1]/11)))
        return result.strip(" ")

    @points.setter
    def points(self,x,y):
        raise TypeError("points is meant to be a private member. use appendpoint instead")



    def appendpoint(self,x,y):
        self.__points.append((x,y))


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

        for i in range(trails_collection_size):
            mitrail=trail(id=i)
            trails_collection.append(mitrail)

        for i in range(cursors_collection_size):
            micursor=cursor(id=i)
            cursors_collection.append(micursor)

        cursors_collection[0].show=False #for tests
        cursors_collection[1].show=True #default cursor


    def monitor_update(self,id):
        """
            updates Monitor interface
        :return:
        
        
        rostopic pub -1 /ged/listener std_msgs/String "cursor_move(0,510.123456,50,true);"
        rostopic pub -1 /ged/listener std_msgs/String "cursor_rotate(0,25.3);"
        rostopic pub -1 /ged/listener std_msgs/String "trail_points(0,'');"
        rostopic pub -1 /ged/listener std_msgs/String "trail_points(0,'0 0 50 50 1000 0');"
        """
        msgs=cursors_collection[id].move(self.pose)

        pubWebMsg=smsg.String()
        for msg in msgs:
            pubWebMsg.data=msg
            self.pubWeb.publish(pubWebMsg)




    def pose_callback(self, data):
        print("pose_callback")
        self.pose = data
        self.pose.x = round(self.pose.x, 4)
        self.pose.y = round(self.pose.y, 4)
        self._feedback.xfeed=self.pose.x
        self._feedback.yfeed=self.pose.y
        self._as.publish_feedback(self._feedback) #keep the client in the loop
        if ( monitor_updates ):
            self.monitor_update(1) #TODO: handle more cursors



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
