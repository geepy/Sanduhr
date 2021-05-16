from sanduhr import Point, Sanduhr

class PcaSimulator:
    def set_angle(self, id, angle):
        print (f'SetAngle #{id}: {angle:3.0f}')

pca = PcaSimulator()
uhr = Sanduhr(pca, 1, 2, 3)
uhr.draw_line(Point(100,500), Point(500,500))