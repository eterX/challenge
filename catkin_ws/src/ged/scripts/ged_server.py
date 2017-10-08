#! /usr/bin/env python
#
# entry point for the Ged client
#
# author: Leandro Batlle
#
#
#std
import sys,math as m,time

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
distance_tolerance=0.2
pose_callback_period=0.1 #[secs]
rospy_Rate=15

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
        result.append(cursor_rotate_template.format(id=str(self.id),theta=int(-theta*360/2/m.pi)))
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

    #switched from polar to cartesian
    #_feedback = gmsg.goToPointPolarFeedback()
    #_result = gmsg.goToPointPolarResult()
    _feedback = gmsg.goToPointFeedback()
    _result = gmsg.goToPointResult()

    def __init__(self, name):
        self._action_name = name

        self.pose = Pose()
        self.pose_callback_last = 0
        self.pubtwist = rospy.Publisher('/ged/turtle1/cmd_vel', geomsg.Twist, queue_size=10)
        self.pubWeb= rospy.Publisher('/ged/listener', smsg.String, queue_size=10)
        self._as = actionlib.SimpleActionServer(self._action_name, gmsg.goToPointAction, execute_cb=self.execute_cb,  auto_start = False)
        self._as.start() #do not replace with auto_start...

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


    def get_distance(self, goal_x, goal_y):
        """
        Proportional Controller (thanks to https://github.com/clebercoutof/turtlesim_cleaner)

        :param goal_x:
        :param goal_y:
        :return: float # distance from current pos to goal
        """
        distance = m.sqrt(pow((goal_x - self.pose.x), 2) + pow((goal_y - self.pose.y), 2))
        return distance



    def pose_callback(self, data):
        #global read-only pose_callback_period
        #cadence of pose msgs processed,
        #TODO: get a ROS-native way for throttling pose updates
        if (self.pose_callback_last +  pose_callback_period  < time.time()):
            print("pose_callback tstamp: {}".format(str(time.time())))

            self.pose = data
            self.pose.x = round(self.pose.x, 4)
            self.pose.y = round(self.pose.y, 4)
            if self._as.current_goal is not None:
                self._feedback.xfeed=self.pose.x
                self._feedback.yfeed=self.pose.y
                self._as.publish_feedback(self._feedback) #keep the client in the loop
            if ( monitor_updates ):
                self.monitor_update(1) #TODO: handle cursors_collection
            self.pose_callback_last=time.time()


    def execute_cb(self, goal):
        # helper variables
        r = rospy.Rate(rospy_Rate)
        success = True
        #Callback function implementing the pose value received

        # publish info to the console for the user
        rospy.loginfo('%s: Executing, ' % (self._action_name))
        self.pose_subscriber = rospy.Subscriber('/ged/turtle1/pose', Pose, self.pose_callback)


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

            #switched from polar to cartesian
            #if goal.ang != 0:
            #    miwist=geomsg.Twist(angular=geomsg.Vector3(z=-goal.ang*2*m.pi/360)) #to rad CW
            #    self.pubtwist.publish(miwist,)
            #if goal.len != 0:
            miwist=geomsg.Twist()
            while m.sqrt(pow((goal.x - self.pose.x), 2) + pow((goal.y - self.pose.y), 2)) >= distance_tolerance:

                #Proportional Controller (thanks to https://github.com/clebercoutof/turtlesim_cleaner)
                #linear velocity in the x-axis:
                miwist.linear.x = 1.5 * m.sqrt(pow((goal.x - self.pose.x), 2) + pow((goal.y - self.pose.y), 2))
                miwist.linear.y = 0
                miwist.linear.z = 0

                #angular velocity in the z-axis:
                miwist.angular.x = 0
                miwist.angular.y = 0
                miwist.angular.z = 4 * (m.atan2(goal.y - self.pose.y, goal.x - self.pose.x) - self.pose.theta)

                #Publishing our vel_msg
                self.pubtwist.publish(miwist)
                r.sleep()
                #self.pose_subscriber.unregister()
            #self.pubtwist.publish(miwist)
            #r.sleep()
            miwist.linear.x = 0
            miwist.angular.z =0
            self.pubtwist.publish(miwist)
            self.pose_subscriber.unregister()

        if success:
            #self._result.result(x=1,y=2)
            #self._result.sequence = self._feedback.sequence
            rospy.loginfo('%s: Succeeded' % self._action_name)
            self._as.set_succeeded(self._result)

if __name__ == '__main__':
    rospy.init_node('ged_server_py',)
    server = gedAction(rospy.get_name())
    rospy.spin()
