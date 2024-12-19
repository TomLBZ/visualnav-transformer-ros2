#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import argparse
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

class RTSPStreamerNode(Node):
    def __init__(self, topic_name, rtsp_link):
        super().__init__('rtsp_streamer')
        self.publisher_ = self.create_publisher(Image, topic_name, 10)
        self.bridge = CvBridge()
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(rtsp_link)
        if not self.cap.isOpened():
            self.get_logger().error(f"Failed to open RTSP stream: {rtsp_link}")
        
        # Create a timer to periodically read and publish frames
        # Adjust frequency as needed, e.g. 30Hz
        self.timer = self.create_timer(1.0/30.0, self.publish_frame)
        
    def publish_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                self.get_logger().warn("Failed to read frame from RTSP stream.")
                return
            # Convert frame (OpenCV) to ROS Image message
            msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            self.publisher_.publish(msg)
        else:
            self.get_logger().warn("RTSP stream is not open.")

def main():
    parser = argparse.ArgumentParser(description='Stream RTSP video to a ROS2 topic.')
    parser.add_argument('-t', '--topic', required=True, help='Name of the sensor_msgs/Image topic.')
    parser.add_argument('-l', '--link', required=True, help='RTSP link to stream from.')
    args = parser.parse_args()

    rclpy.init()
    node = RTSPStreamerNode(topic_name=args.topic, rtsp_link=args.link)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cap.release()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
