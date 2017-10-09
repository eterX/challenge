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
from turtlesim.srv import *

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
debug_teleport = True
cursors_collection_size = 10
trails_collection_size = 10
cursors_collection=list() #global... 
trails_collection=list()
cursor_move_template="cursor_move({id},{x},{y},{show});"
cursor_rotate_template="cursor_rotate({id},{theta});"
trail_points_template="trail_points({id},{points});"
distance_tolerance=0.5
pose_callback_period=0.1 #[secs]
rospy_Rate=1

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
        for point in self._trail__points:
            result+=" "+str(int(point[0]*1000/11)) #TODO: send this to a "representation layer"
            result+=" "+str(int(1000*(1-point[1]/11)))
        return result.strip(" ")

    @points.setter
    def points(self,x,y):
        raise TypeError("points is meant to be a private member. use appendpoint instead")



    def appendpoint(self,x,y):
        if len(self._trail__points) > 0:
            if (x,y) != self._trail__points[-1]:
                self._trail__points.append((x,y))
        else:
                self.__points.append((x,y))



class gedAction(object):
    # create messages that are used to publish feedback/result
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
        self.pose_subscriber = rospy.Subscriber('/ged/turtle1/pose', Pose, self.pose_callback)
        self.r = rospy.Rate(rospy_Rate)


        for i in range(trails_collection_size):
            mitrail=trail(id=i)
            trails_collection.append(mitrail)

        for i in range(cursors_collection_size):
            micursor=cursor(id=i)
            cursors_collection.append(micursor)

        cursors_collection[0].show=False #for tests
        cursors_collection[1].show=True #default cursor

        self._as = actionlib.SimpleActionServer(self._action_name, gmsg.goToPointAction, execute_cb=self.execute_cb,  auto_start = False)
        self._as.start() #do not replace with auto_start...


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
        distance = math.sqrt(pow((goal_x - self.pose.x), 2) + pow((goal_y - self.pose.y), 2))
        return distance



    def pose_callback(self, data):
        #global read-only pose_callback_period
        #cadence of pose msgs processed,
        #TODO: get a ROS-native way for throttling pose updates

        self.pose = data
        self.pose.x = round(self.pose.x, 4)
        self.pose.y = round(self.pose.y, 4)
        if (self.pose_callback_last +  pose_callback_period  < time.time()):
            #print("pose_callback tstamp: {}".format(str(time.time())))
            if self._as.current_goal.goal is not None:
                self._feedback.xfeed=self.pose.x
                self._feedback.yfeed=self.pose.y
                self._as.publish_feedback(self._feedback) #keep the client in the loop
            if ( monitor_updates ):
                #  and ( self.pose.x != self.pose_x_monitor_last or
                #                                self.pose.y != self.pose_y_monitor_last or
                #                                self.pose.x != self.pose_theta_monitor_last)):
                # self.pose_x_monitor_last = self.pose.x
                # self.pose_y_monitor_last = self.pose.y
                # self.pose_theta_monitor_last = self.pose.theta
                self.monitor_update(1) #TODO: handle cursors_collection
            self.pose_callback_last=time.time()


    def execute_cb(self, goal):
        # helper variables
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
            #mitwist=geomsg.Twist(linear=geomsg.Vector3(x=goal.len),angular=geomsg.Vector3(x=goal.ang))

            #switched from polar to cartesian
            #if goal.ang != 0:
            #    mitwist=geomsg.Twist(angular=geomsg.Vector3(z=-goal.ang*2*math.pi/360)) #to rad CW
            #    self.pubtwist.publish(mitwist,)
            #if goal.len != 0:
            mitwist=geomsg.Twist()
            i_msg=0
            i_msg_max=10
            if not debug_teleport:
                while (self.get_distance(goal.x,goal.y) > distance_tolerance) and (i_msg < i_msg_max):
                    i_msg+=1
                    #print(goal.x,goal.y, self.pose.x, self.pose.y, distance_tolerance, self.get_distance(goal.x,goal.y))

                    #Proportional Controller (thanks to https://github.com/clebercoutof/turtlesim_cleaner)
                    #linear velocity in the x-axis:
                    mitwist.linear.x = 1.5 * math.sqrt(pow((goal.x - self.pose.x), 2) + pow((goal.y - self.pose.y), 2))
                    mitwist.linear.y = 0
                    mitwist.linear.z = 0
                    #angular velocity in the z-axis:
                    mitwist.angular.x = 0
                    mitwist.angular.y = 0
                    mitwist.angular.z = 4 * (math.atan2(goal.y - self.pose.y, goal.x - self.pose.x) - self.pose.theta)

                    #Publishing our vel_msg
                    self.pubtwist.publish(mitwist)
                    self.r.sleep()

            if (self.get_distance(goal.x,goal.y) > distance_tolerance):
                # looks like there is a problem that makes P controller go into infinite loops, until it's fixed, teleporting
                rospy.wait_for_service('/ged/turtle1/teleport_absolute')
                try:
                    teleport = rospy.ServiceProxy('/ged/turtle1/teleport_absolute', TeleportAbsolute)
                    response = teleport(goal.x,goal.y,0)
                    print("Teleport response: {}".format(response))
                    rospy.logwarn("Teleported: {}".format(response))
                    self.pose_callback(self, self.pose)
                    time.sleep(2)
                except rospy.ServiceException, e:
                    print "Service call failed: %s"%e



                    #self.pubtwist.publish(mitwist)
                    #r.sleep()
                    #mitwist.linear.x = 0
                    #mitwist.angular.z =0
                    #self.pubtwist.publish(mitwist)

        if success:
            #self._result.result(x=1,y=2)
            #self._result.sequence = self._feedback.sequence
            rospy.loginfo('%s: Succeeded' % self._action_name)
            self._as.set_succeeded(self._result)

if __name__ == '__main__':
    rospy.init_node('ged_server_py',)
    server = gedAction(rospy.get_name())
    rospy.spin()
