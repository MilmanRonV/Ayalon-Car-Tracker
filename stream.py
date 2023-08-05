import cv2

from geometry import Coordinate, Line, draw_line
from tracker import ObjectTracker


class CarStream:
    def __init__(self, cap, tracker):
        self.cap = cap
        self.tracker = tracker

        self.obj_detector = cv2.createBackgroundSubtractorMOG2(
            history=100, varThreshold=150
        )  # TODO: explore other detection algorithms

    def run(self):
        if self.cap.isOpened():
            while True:
                ret, frame = self.cap.read()

                if ret:
                    mask = self.obj_detector.apply(frame)
                    contours, _ = cv2.findContours(
                        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
                    )
                    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 500]

                    # eliminate double detection
                    for i, cnt in enumerate(contours[:-1]):
                        x, y, w, h = cv2.boundingRect(cnt)
                        c1 = Coordinate(x + int(w / 2), y + int(h / 2))
                        for j, cnt2 in enumerate(contours[i + 1 : -1]):
                            x, y, w, h = cv2.boundingRect(cnt2)
                            c2 = Coordinate(x + int(w / 2), y + int(h / 2))
                            if c1.distance(c2) < 30:
                                contours[j + i + 1] = cnt

                    for cnt in contours:
                        x, y, w, h = cv2.boundingRect(cnt)
                        cv2.drawContours(
                            mask,
                            contours,
                            -1,
                            color=(255, 255, 255),
                            thickness=cv2.FILLED,
                        )
                        cv2.circle(
                            frame, (x + int(w / 2), y + int(h / 2)), 3, (0, 0, 255), 3
                        )

                        object_num = ot.track(
                            Coordinate(x + int(w / 2), y + int(h / 2))
                        ).id
                        cv2.putText(
                            frame,
                            str(object_num),
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (36, 255, 12),
                            2,
                        )

                    cv2.putText(
                        frame,
                        str(ot.passed_objects),
                        (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (36, 255, 12),
                        2,
                    )

                    draw_line(frame, ot.starting_line)

                    cv2.imshow("mask", mask)
                    cv2.imshow("Livestream", frame)

                    # Press 'q' to quit
                    if cv2.waitKey(30) & 0xFF == ord("q"):
                        break

                else:
                    # If no frame was read, the livestream has ended or encountered an error
                    break

            self.cap.release()
            cv2.destroyAllWindows()
        else:
            print("Failed to open the livestream capture. Try again later.")


if __name__ == "__main__":
    livestream_url = "https://5e0da72d486c5.streamlock.net:8443/ayalon/Mozes_Gantry.stream/playlist.m3u8"
    # the camera tends to move in random directions from time to time, accuracy may vary...

    cap = cv2.VideoCapture(livestream_url)

    l1 = Line((0, 550), 1)
    ot = ObjectTracker(l1)

    stream = CarStream(cap, ot)
    stream.run()
