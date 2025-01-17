import math


class Reward:
    def __init__(self, verbose=False):
        #self.first_racingpoint_index = None
        self.first_racingpoint_index = 0
        self.verbose = verbose

    def reward_function(self, params):

        ################## HELPER FUNCTIONS ###################

        def dist_2_points(x1, x2, y1, y2):
            return abs(abs(x1-x2)**2 + abs(y1-y2)**2)**0.5

        def closest_2_racing_points_index(racing_coords, car_coords):

            # Calculate all distances to racing points
            distances = []
            for i in range(len(racing_coords)):
                distance = dist_2_points(x1=racing_coords[i][0], x2=car_coords[0],
                                         y1=racing_coords[i][1], y2=car_coords[1])
                distances.append(distance)

            # Get index of the closest racing point
            closest_index = distances.index(min(distances))

            # Get index of the second closest racing point
            distances_no_closest = distances.copy()
            distances_no_closest[closest_index] = 999
            second_closest_index = distances_no_closest.index(
                min(distances_no_closest))

            return [closest_index, second_closest_index]

        def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):

            # Calculate the distances between 2 closest racing points
            a = abs(dist_2_points(x1=closest_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=closest_coords[1],
                                  y2=second_closest_coords[1]))

            # Distances between car and closest and second closest racing point
            b = abs(dist_2_points(x1=car_coords[0],
                                  x2=closest_coords[0],
                                  y1=car_coords[1],
                                  y2=closest_coords[1]))
            c = abs(dist_2_points(x1=car_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=car_coords[1],
                                  y2=second_closest_coords[1]))

            # Calculate distance between car and racing line (goes through 2 closest racing points)
            # try-except in case a=0 (rare bug in DeepRacer)
            try:
                distance = abs(-(a**4) + 2*(a**2)*(b**2) + 2*(a**2)*(c**2) -
                               (b**4) + 2*(b**2)*(c**2) - (c**4))**0.5 / (2*a)
            except:
                distance = b

            return distance

        # Calculate which one of the closest racing points is the next one and which one the previous one
        def next_prev_racing_point(closest_coords, second_closest_coords, car_coords, heading):

            # Virtually set the car more into the heading direction
            heading_vector = [math.cos(math.radians(
                heading)), math.sin(math.radians(heading))]
            new_car_coords = [car_coords[0]+heading_vector[0],
                              car_coords[1]+heading_vector[1]]

            # Calculate distance from new car coords to 2 closest racing points
            distance_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                        x2=closest_coords[0],
                                                        y1=new_car_coords[1],
                                                        y2=closest_coords[1])
            distance_second_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                               x2=second_closest_coords[0],
                                                               y1=new_car_coords[1],
                                                               y2=second_closest_coords[1])

            if distance_closest_coords_new <= distance_second_closest_coords_new:
                next_point_coords = closest_coords
                prev_point_coords = second_closest_coords
            else:
                next_point_coords = second_closest_coords
                prev_point_coords = closest_coords

            return [next_point_coords, prev_point_coords]

        def racing_direction_diff(closest_coords, second_closest_coords, car_coords, heading):

            # Calculate the direction of the center line based on the closest waypoints
            next_point, prev_point = next_prev_racing_point(closest_coords,
                                                            second_closest_coords,
                                                            car_coords,
                                                            heading)

            # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
            track_direction = math.atan2(
                next_point[1] - prev_point[1], next_point[0] - prev_point[0])

            # Convert to degree
            track_direction = math.degrees(track_direction)

            # Calculate the difference between the track direction and the heading direction of the car
            direction_diff = abs(track_direction - heading)
            if direction_diff > 180:
                direction_diff = 360 - direction_diff

            return direction_diff

        # Gives back indexes that lie between start and end index of a cyclical list
        # (start index is included, end index is not)
        def indexes_cyclical(start, end, array_len):

            if end < start:
                end += array_len

            return [index % array_len for index in range(start, end)]

        # Calculate how long car would take for entire lap, if it continued like it did until now
        def projected_time(first_index, closest_index, step_count, times_list):

            # Calculate how much time has passed since start
            current_actual_time = (step_count-1) / 15

            # Calculate which indexes were already passed
            indexes_traveled = indexes_cyclical(
                first_index, closest_index, len(times_list))

            # Calculate how much time should have passed if car would have followed optimals
            current_expected_time = sum(
                [times_list[i] for i in indexes_traveled])

            # Calculate how long one entire lap takes if car follows optimals
            total_expected_time = sum(times_list)

            # Calculate how long car would take for entire lap, if it continued like it did until now
            try:
                projected_time = (current_actual_time /
                                  current_expected_time) * total_expected_time
            except:
                projected_time = 9999

            return projected_time

        #################### RACING LINE ######################

        # Optimal racing line
        # Each row: [x,y,speed,timeFromPreviousPoint]
        racing_track = [[1.3336, -2.79743, 4.0, 0.03755],
                        [1.1834, -2.79489, 4.0, 0.03755],
                        [1.03321, -2.79187, 4.0, 0.03756],
                        [0.88303, -2.7884, 4.0, 0.03756],
                        [0.73286, -2.78448, 4.0, 0.03756],
                        [0.5827, -2.78011, 4.0, 0.03756],
                        [0.43255, -2.77529, 4.0, 0.03756],
                        [0.28242, -2.77004, 4.0, 0.03756],
                        [0.1323, -2.76436, 4.0, 0.03756],
                        [-0.0178, -2.75825, 4.0, 0.03756],
                        [-0.16789, -2.75171, 4.0, 0.03756],
                        [-0.31795, -2.74474, 4.0, 0.03756],
                        [-0.468, -2.73735, 4.0, 0.03756],
                        [-0.61802, -2.72955, 4.0, 0.03756],
                        [-0.76802, -2.72132, 4.0, 0.03756],
                        [-0.918, -2.71267, 4.0, 0.03756],
                        [-1.06795, -2.7036, 4.0, 0.03756],
                        [-1.21787, -2.6941, 4.0, 0.03756],
                        [-1.36777, -2.68419, 4.0, 0.03756],
                        [-1.51763, -2.67385, 4.0, 0.03756],
                        [-1.66747, -2.66308, 4.0, 0.03756],
                        [-1.81727, -2.65189, 4.0, 0.03756],
                        [-1.96704, -2.64026, 4.0, 0.03755],
                        [-2.11677, -2.62819, 4.0, 0.03755],
                        [-2.26646, -2.61567, 4.0, 0.03755],
                        [-2.41612, -2.6027, 4.0, 0.03755],
                        [-2.56572, -2.58928, 4.0, 0.03755],
                        [-2.71528, -2.57538, 4.0, 0.03755],
                        [-2.86479, -2.56101, 4.0, 0.03755],
                        [-3.01424, -2.54615, 4.0, 0.03755],
                        [-3.16363, -2.53078, 4.0, 0.03754],
                        [-3.31294, -2.51489, 4.0, 0.03754],
                        [-3.46218, -2.49847, 4.0, 0.03753],
                        [-3.61133, -2.48149, 4.0, 0.03753],
                        [-3.76036, -2.46393, 4.0, 0.03752],
                        [-3.90927, -2.44576, 4.0, 0.0375],
                        [-4.05803, -2.42694, 4.0, 0.03749],
                        [-4.2066, -2.40744, 4.0, 0.03746],
                        [-4.35494, -2.3872, 4.0, 0.03743],
                        [-4.50301, -2.36619, 4.0, 0.03739],
                        [-4.65074, -2.34432, 4.0, 0.03734],
                        [-4.79807, -2.32155, 4.0, 0.03727],
                        [-4.94489, -2.29777, 4.0, 0.03718],
                        [-5.0911, -2.27291, 4.0, 0.03708],
                        [-5.23659, -2.24686, 4.0, 0.03695],
                        [-5.38122, -2.21951, 4.0, 0.0368],
                        [-5.52484, -2.19076, 4.0, 0.03662],
                        [-5.66727, -2.16048, 4.0, 0.0364],
                        [-5.80835, -2.12854, 4.0, 0.03616],
                        [-5.94788, -2.09483, 4.0, 0.03589],
                        [-6.08569, -2.05923, 4.0, 0.03558],
                        [-6.22158, -2.02165, 4.0, 0.03525],
                        [-6.3554, -1.98199, 4.0, 0.03489],
                        [-6.48699, -1.94019, 4.0, 0.03452],
                        [-6.61622, -1.8962, 4.0, 0.03413],
                        [-6.74299, -1.85002, 4.0, 0.03373],
                        [-6.86724, -1.80164, 3.84731, 0.03466],
                        [-6.98891, -1.75108, 3.50957, 0.03754],
                        [-7.10781, -1.69828, 3.1778, 0.04094],
                        [-7.22381, -1.64319, 2.85631, 0.04496],
                        [-7.3365, -1.58558, 2.55026, 0.04963],
                        [-7.44545, -1.52523, 2.22393, 0.056],
                        [-7.55011, -1.46186, 1.95714, 0.06251],
                        [-7.64978, -1.39514, 1.71683, 0.06986],
                        [-7.74357, -1.32468, 1.503, 0.07805],
                        [-7.83038, -1.25006, 1.31243, 0.08723],
                        [-7.90882, -1.17082, 1.31243, 0.08496],
                        [-7.97676, -1.08638, 1.31243, 0.08258],
                        [-8.0317, -0.99642, 1.31243, 0.08031],
                        [-8.07031, -0.90105, 1.31243, 0.0784],
                        [-8.08796, -0.80139, 1.31243, 0.07712],
                        [-8.07832, -0.70155, 1.39178, 0.07207],
                        [-8.04523, -0.6069, 1.57113, 0.06382],
                        [-7.9943, -0.51909, 1.72525, 0.05884],
                        [-7.92854, -0.43868, 1.89566, 0.05479],
                        [-7.85022, -0.36579, 2.10002, 0.05095],
                        [-7.76124, -0.30018, 2.35194, 0.04701],
                        [-7.66332, -0.24132, 2.65149, 0.04309],
                        [-7.55799, -0.18849, 3.06526, 0.03844],
                        [-7.44683, -0.14069, 3.6229, 0.0334],
                        [-7.33129, -0.0968, 4.0, 0.0309],
                        [-7.21261, -0.05581, 4.0, 0.03139],
                        [-7.09154, -0.01661, 4.0, 0.03181],
                        [-6.96174, 0.02782, 4.0, 0.0343],
                        [-6.83234, 0.07454, 4.0, 0.03439],
                        [-6.70367, 0.12344, 4.0, 0.03441],
                        [-6.57584, 0.17457, 4.0, 0.03442],
                        [-6.44901, 0.2281, 4.0, 0.03442],
                        [-6.32336, 0.28423, 4.0, 0.03441],
                        [-6.19911, 0.34332, 4.0, 0.0344],
                        [-6.07645, 0.40554, 4.0, 0.03438],
                        [-5.95555, 0.47107, 4.0, 0.03438],
                        [-5.83666, 0.54022, 4.0, 0.03438],
                        [-5.72, 0.61318, 4.0, 0.0344],
                        [-5.6057, 0.69007, 4.0, 0.03444],
                        [-5.4939, 0.77093, 4.0, 0.03449],
                        [-5.38468, 0.85575, 4.0, 0.03457],
                        [-5.27808, 0.94447, 4.0, 0.03467],
                        [-5.17411, 1.03697, 4.0, 0.03479],
                        [-5.07274, 1.13309, 4.0, 0.03492],
                        [-4.97391, 1.23261, 4.0, 0.03506],
                        [-4.87752, 1.33528, 4.0, 0.03521],
                        [-4.78344, 1.44082, 4.0, 0.03535],
                        [-4.69149, 1.54891, 4.0, 0.03548],
                        [-4.6015, 1.6592, 4.0, 0.03559],
                        [-4.51326, 1.77136, 4.0, 0.03568],
                        [-4.42657, 1.88504, 4.0, 0.03574],
                        [-4.34127, 1.99991, 4.0, 0.03577],
                        [-4.25726, 2.1156, 4.0, 0.03574],
                        [-4.17451, 2.2317, 4.0, 0.03564],
                        [-4.09294, 2.34779, 3.73557, 0.03798],
                        [-4.01231, 2.46364, 3.31296, 0.0426],
                        [-3.93347, 2.57631, 2.84095, 0.0484],
                        [-3.8537, 2.68725, 2.51066, 0.05443],
                        [-3.77227, 2.79517, 2.17268, 0.06222],
                        [-3.6885, 2.89888, 1.76306, 0.07562],
                        [-3.6017, 2.99719, 1.76306, 0.07439],
                        [-3.51126, 3.08897, 1.76306, 0.07309],
                        [-3.41625, 3.17223, 1.76306, 0.07165],
                        [-3.316, 3.24497, 1.76306, 0.07025],
                        [-3.2098, 3.30401, 1.76306, 0.06892],
                        [-3.09721, 3.34235, 1.94557, 0.06113],
                        [-2.9818, 3.36379, 2.14648, 0.05469],
                        [-2.86545, 3.37149, 2.29037, 0.05091],
                        [-2.74922, 3.36724, 2.44498, 0.04757],
                        [-2.6338, 3.35254, 2.59529, 0.04483],
                        [-2.51964, 3.3286, 2.61582, 0.04459],
                        [-2.40708, 3.29615, 2.61582, 0.04478],
                        [-2.29635, 3.25594, 2.61582, 0.04504],
                        [-2.18768, 3.2083, 2.61582, 0.04536],
                        [-2.08159, 3.15271, 2.61582, 0.04579],
                        [-1.9788, 3.08847, 2.61582, 0.04634],
                        [-1.88018, 3.01486, 2.91654, 0.0422],
                        [-1.78541, 2.93362, 3.18941, 0.03914],
                        [-1.69422, 2.84594, 3.47973, 0.03636],
                        [-1.6063, 2.75275, 3.80081, 0.03371],
                        [-1.52134, 2.65492, 4.0, 0.03239],
                        [-1.43896, 2.55324, 4.0, 0.03272],
                        [-1.35882, 2.44838, 4.0, 0.03299],
                        [-1.2806, 2.3409, 4.0, 0.03323],
                        [-1.20392, 2.23138, 4.0, 0.03342],
                        [-1.12842, 2.12034, 4.0, 0.03357],
                        [-1.05387, 2.00809, 3.65047, 0.03691],
                        [-0.98165, 1.89727, 3.20033, 0.04133],
                        [-0.90875, 1.78744, 2.81693, 0.04679],
                        [-0.83453, 1.67959, 2.42404, 0.05401],
                        [-0.75835, 1.57467, 2.11162, 0.0614],
                        [-0.6796, 1.47366, 2.11162, 0.06065],
                        [-0.59766, 1.37764, 2.11162, 0.05978],
                        [-0.51187, 1.2879, 2.11162, 0.05879],
                        [-0.42154, 1.20605, 2.11162, 0.05773],
                        [-0.3258, 1.13461, 2.11162, 0.05657],
                        [-0.22423, 1.07667, 2.16661, 0.05397],
                        [-0.11839, 1.03143, 2.05229, 0.05609],
                        [-0.00935, 0.99867, 2.05229, 0.05548],
                        [0.10184, 0.97737, 2.05229, 0.05517],
                        [0.21449, 0.96704, 2.05229, 0.05512],
                        [0.32801, 0.96828, 2.05229, 0.05532],
                        [0.44175, 0.98125, 2.05229, 0.05578],
                        [0.55469, 1.00894, 2.11294, 0.05503],
                        [0.66559, 1.05095, 2.32409, 0.05103],
                        [0.77384, 1.10525, 2.56422, 0.04723],
                        [0.87926, 1.17002, 2.83303, 0.04367],
                        [0.98187, 1.24376, 3.13957, 0.04024],
                        [1.08183, 1.3251, 3.53993, 0.03641],
                        [1.17948, 1.41266, 3.94795, 0.03322],
                        [1.2751, 1.50544, 4.0, 0.03331],
                        [1.36905, 1.6024, 4.0, 0.03375],
                        [1.46171, 1.70251, 4.0, 0.0341],
                        [1.55351, 1.80475, 4.0, 0.03435],
                        [1.64488, 1.90801, 4.0, 0.03447],
                        [1.74129, 2.01583, 4.0, 0.03616],
                        [1.83849, 2.12315, 4.0, 0.0362],
                        [1.93664, 2.2298, 4.0, 0.03623],
                        [2.03586, 2.33555, 4.0, 0.03625],
                        [2.13632, 2.44016, 4.0, 0.03626],
                        [2.2382, 2.54331, 4.0, 0.03625],
                        [2.34159, 2.64476, 4.0, 0.03621],
                        [2.44658, 2.74427, 4.0, 0.03616],
                        [2.55329, 2.84153, 4.0, 0.0361],
                        [2.66184, 2.93622, 4.0, 0.03601],
                        [2.77232, 3.02806, 4.0, 0.03592],
                        [2.88477, 3.11678, 4.0, 0.03581],
                        [2.99919, 3.20212, 4.0, 0.03569],
                        [3.11558, 3.28386, 4.0, 0.03556],
                        [3.23389, 3.36175, 4.0, 0.03541],
                        [3.35406, 3.43558, 4.0, 0.03526],
                        [3.47598, 3.50515, 4.0, 0.03509],
                        [3.59954, 3.57029, 4.0, 0.03492],
                        [3.72461, 3.63083, 4.0, 0.03474],
                        [3.85103, 3.68666, 4.0, 0.03455],
                        [3.97864, 3.73774, 4.0, 0.03436],
                        [4.10726, 3.78406, 4.0, 0.03418],
                        [4.23673, 3.82574, 4.0, 0.034],
                        [4.36687, 3.86304, 3.656, 0.03703],
                        [4.49752, 3.89623, 3.29935, 0.04086],
                        [4.62859, 3.92525, 2.9265, 0.04587],
                        [4.75996, 3.95001, 2.58656, 0.05168],
                        [4.89153, 3.97039, 2.39707, 0.05554],
                        [5.02318, 3.98569, 2.39707, 0.05529],
                        [5.15476, 3.99491, 2.39707, 0.05502],
                        [5.28597, 3.99675, 2.39707, 0.05474],
                        [5.41634, 3.98935, 2.39707, 0.05447],
                        [5.54507, 3.97031, 2.39707, 0.05429],
                        [5.6712, 3.93787, 3.58537, 0.03632],
                        [5.79601, 3.89944, 4.0, 0.03265],
                        [5.91982, 3.85641, 4.0, 0.03277],
                        [6.04288, 3.80974, 4.0, 0.0329],
                        [6.16543, 3.76042, 4.0, 0.03302],
                        [6.28766, 3.70936, 4.0, 0.03312],
                        [6.40992, 3.65719, 4.0, 0.03323],
                        [6.5353, 3.60465, 4.0, 0.03399],
                        [6.66094, 3.55284, 4.0, 0.03398],
                        [6.78664, 3.50173, 4.0, 0.03392],
                        [6.91234, 3.45127, 4.0, 0.03386],
                        [7.03801, 3.40141, 4.0, 0.0338],
                        [7.16363, 3.3521, 4.0, 0.03374],
                        [7.28918, 3.30333, 3.56884, 0.03774],
                        [7.41466, 3.25509, 2.86306, 0.04695],
                        [7.54003, 3.20742, 2.42803, 0.05524],
                        [7.66526, 3.16036, 2.11187, 0.06335],
                        [7.77965, 3.11796, 1.85449, 0.06578],
                        [7.89195, 3.07362, 1.85449, 0.0651],
                        [7.99999, 3.02544, 1.85449, 0.06379],
                        [8.10167, 2.97182, 1.85449, 0.06199],
                        [8.19487, 2.91156, 1.83683, 0.06042],
                        [8.27734, 2.84392, 1.74303, 0.06119],
                        [8.3465, 2.76867, 1.60769, 0.06357],
                        [8.4038, 2.68789, 1.47131, 0.06731],
                        [8.44998, 2.60281, 1.3, 0.07447],
                        [8.4851, 2.51422, 1.3, 0.0733],
                        [8.5082, 2.42273, 1.3, 0.07259],
                        [8.51794, 2.32911, 1.3, 0.0724],
                        [8.51172, 2.23448, 1.3, 0.07295],
                        [8.48573, 2.14094, 1.3, 0.07468],
                        [8.43309, 2.05391, 1.64924, 0.06167],
                        [8.36332, 1.97448, 1.83663, 0.05756],
                        [8.27916, 1.90331, 2.03924, 0.05405],
                        [8.18273, 1.84061, 2.27608, 0.05054],
                        [8.07595, 1.78615, 2.53912, 0.04721],
                        [7.96047, 1.7395, 2.89478, 0.04302],
                        [7.83802, 1.69975, 3.28385, 0.0392],
                        [7.70996, 1.66597, 3.82829, 0.03459],
                        [7.57765, 1.63698, 4.0, 0.03386],
                        [7.44248, 1.61137, 4.0, 0.0344],
                        [7.30585, 1.58751, 4.0, 0.03467],
                        [7.16806, 1.56221, 4.0, 0.03502],
                        [7.03117, 1.53555, 4.0, 0.03486],
                        [6.89543, 1.50723, 3.97095, 0.03492],
                        [6.76113, 1.47689, 3.56309, 0.03864],
                        [6.62861, 1.44418, 3.16952, 0.04307],
                        [6.4982, 1.40875, 2.83393, 0.04768],
                        [6.37026, 1.3703, 2.47566, 0.05396],
                        [6.24517, 1.32849, 2.17287, 0.0607],
                        [6.12368, 1.28263, 1.92798, 0.06736],
                        [6.0066, 1.23204, 1.68373, 0.07575],
                        [5.89501, 1.17591, 1.68373, 0.07419],
                        [5.79015, 1.11346, 1.68373, 0.07248],
                        [5.69396, 1.0436, 1.68373, 0.07061],
                        [5.60886, 0.96541, 1.68373, 0.06864],
                        [5.53775, 0.87851, 1.68373, 0.06669],
                        [5.48513, 0.78338, 1.79399, 0.0606],
                        [5.44875, 0.684, 1.89104, 0.05597],
                        [5.42661, 0.58274, 1.9708, 0.05259],
                        [5.41716, 0.48105, 1.82655, 0.05592],
                        [5.41954, 0.3799, 1.65264, 0.06122],
                        [5.43308, 0.28013, 1.48345, 0.06787],
                        [5.45738, 0.18249, 1.48345, 0.06782],
                        [5.49278, 0.08799, 1.48345, 0.06803],
                        [5.53961, -0.00221, 1.48345, 0.06851],
                        [5.59956, -0.086, 1.48345, 0.06945],
                        [5.67511, -0.1597, 1.48345, 0.07115],
                        [5.76883, -0.21667, 1.88833, 0.05808],
                        [5.87291, -0.26087, 2.11329, 0.05351],
                        [5.9851, -0.29343, 2.40006, 0.04867],
                        [6.10355, -0.31585, 2.67948, 0.04499],
                        [6.22705, -0.32927, 3.01935, 0.04114],
                        [6.35455, -0.33492, 3.45836, 0.0369],
                        [6.48512, -0.33418, 4.0, 0.03264],
                        [6.61792, -0.32856, 4.0, 0.03323],
                        [6.75218, -0.31961, 3.77813, 0.03561],
                        [6.88717, -0.30897, 3.4724, 0.039],
                        [7.02364, -0.30056, 3.1077, 0.044],
                        [7.15871, -0.29534, 2.80038, 0.04827],
                        [7.29201, -0.29401, 2.51656, 0.05297],
                        [7.4231, -0.29734, 2.25811, 0.05807],
                        [7.5515, -0.30602, 1.97591, 0.06513],
                        [7.67674, -0.32066, 1.73308, 0.07276],
                        [7.79803, -0.34224, 1.73308, 0.07109],
                        [7.91445, -0.3717, 1.73308, 0.06929],
                        [8.02477, -0.41003, 1.73308, 0.06739],
                        [8.12742, -0.45822, 1.73308, 0.06543],
                        [8.21983, -0.51762, 1.73308, 0.06338],
                        [8.29838, -0.58903, 1.72822, 0.06142],
                        [8.3661, -0.66798, 1.56736, 0.06636],
                        [8.42303, -0.75335, 1.56736, 0.06547],
                        [8.46891, -0.8443, 1.56736, 0.06499],
                        [8.5032, -0.94006, 1.56736, 0.06489],
                        [8.52416, -1.04012, 1.56736, 0.06523],
                        [8.529, -1.14369, 1.56736, 0.06615],
                        [8.51298, -1.24881, 1.73259, 0.06137],
                        [8.47889, -1.35253, 1.89712, 0.05755],
                        [8.42902, -1.45317, 2.06864, 0.0543],
                        [8.36528, -1.54974, 2.28128, 0.05072],
                        [8.28967, -1.64176, 2.47434, 0.04813],
                        [8.20359, -1.72893, 2.68355, 0.04565],
                        [8.10832, -1.81113, 2.88616, 0.0436],
                        [8.00494, -1.88828, 3.09661, 0.04166],
                        [7.89442, -1.96039, 3.31931, 0.03976],
                        [7.77766, -2.02758, 3.55421, 0.0379],
                        [7.65549, -2.09, 3.80003, 0.0361],
                        [7.52869, -2.14785, 4.0, 0.03484],
                        [7.39793, -2.20138, 4.0, 0.03532],
                        [7.26384, -2.25084, 4.0, 0.03573],
                        [7.12685, -2.29638, 4.0, 0.03609],
                        [6.98756, -2.33842, 4.0, 0.03637],
                        [6.84635, -2.37722, 4.0, 0.03661],
                        [6.70356, -2.41305, 4.0, 0.0368],
                        [6.55948, -2.44616, 4.0, 0.03696],
                        [6.41435, -2.47678, 4.0, 0.03708],
                        [6.26836, -2.50513, 4.0, 0.03718],
                        [6.12167, -2.53141, 4.0, 0.03726],
                        [5.9744, -2.55577, 4.0, 0.03732],
                        [5.82666, -2.57838, 4.0, 0.03736],
                        [5.67854, -2.59937, 4.0, 0.0374],
                        [5.53009, -2.61887, 4.0, 0.03743],
                        [5.38138, -2.63698, 4.0, 0.03745],
                        [5.23244, -2.6538, 4.0, 0.03747],
                        [5.08332, -2.66941, 4.0, 0.03749],
                        [4.93403, -2.68389, 4.0, 0.0375],
                        [4.78461, -2.6973, 4.0, 0.03751],
                        [4.63507, -2.7097, 4.0, 0.03751],
                        [4.48543, -2.72115, 4.0, 0.03752],
                        [4.3357, -2.7317, 4.0, 0.03752],
                        [4.1859, -2.74139, 4.0, 0.03753],
                        [4.03603, -2.75025, 4.0, 0.03753],
                        [3.88611, -2.75832, 4.0, 0.03754],
                        [3.73613, -2.76563, 4.0, 0.03754],
                        [3.58612, -2.77222, 4.0, 0.03754],
                        [3.43607, -2.7781, 4.0, 0.03754],
                        [3.28598, -2.78331, 4.0, 0.03754],
                        [3.13587, -2.78786, 4.0, 0.03754],
                        [2.98574, -2.79177, 4.0, 0.03755],
                        [2.83559, -2.79506, 4.0, 0.03755],
                        [2.68542, -2.79776, 4.0, 0.03755],
                        [2.53524, -2.79987, 4.0, 0.03755],
                        [2.38504, -2.80141, 4.0, 0.03755],
                        [2.23484, -2.8024, 4.0, 0.03755],
                        [2.08464, -2.80285, 4.0, 0.03755],
                        [1.93443, -2.80277, 4.0, 0.03755],
                        [1.78422, -2.80218, 4.0, 0.03755],
                        [1.63401, -2.80108, 4.0, 0.03755],
                        [1.4838, -2.79949, 4.0, 0.03755]]

        ################## INPUT PARAMETERS ###################

        # Read all input parameters
        # 全ての入力パラメータを読み込む
        all_wheels_on_track = params['all_wheels_on_track']
        x = params['x']
        y = params['y']
        distance_from_center = params['distance_from_center']
        is_left_of_center = params['is_left_of_center']
        heading = params['heading']
        progress = params['progress']
        steps = params['steps']
        speed = params['speed']
        steering_angle = params['steering_angle']
        track_width = params['track_width']
        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        is_offtrack = params['is_offtrack']

        ############### OPTIMAL X,Y,SPEED,TIME ################

        # Get closest indexes for racing line (and distances to all points on racing line)
        # レーシングラインに最も近いインデックスを取得 (およびレーシングライン上のすべての点までの距離も取得)
        closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [x, y])

        # Get optimal [x, y, speed, time] for closest and second closest index
        optimals = racing_track[closest_index]
        optimals_second = racing_track[second_closest_index]

        # Save first racingpoint of episode for later
        # エピソードの最初のレーシングポイントを保存しておく
        if self.verbose == True:
            self.first_racingpoint_index = 0  # this is just for testing purposes
        if steps == 1:
            self.first_racingpoint_index = closest_index

        ################ REWARD AND PUNISHMENT ################

        ## Define the default reward ##
        reward = 1

        ## Reward if car goes close to optimal racing line ##
        ## 最適なレーシングラインに近づくと報酬がもらえる ##
        DISTANCE_MULTIPLE = 1
        dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [x, y])
        distance_reward = max(1e-3, 1 - (dist/(track_width*0.5)))
        reward += distance_reward * DISTANCE_MULTIPLE

        ## Reward if speed is close to optimal speed ##
        ## 最適な速度に近づいたら報酬を与える ##
        SPEED_DIFF_NO_REWARD = 1
        SPEED_MULTIPLE = 2
        speed_diff = abs(optimals[2]-speed)
        if speed_diff <= SPEED_DIFF_NO_REWARD:
            # we use quadratic punishment (not linear) bc we're not as confident with the optimal speed
            # so, we do not punish small deviations from optimal speed
            speed_reward = (1 - (speed_diff/(SPEED_DIFF_NO_REWARD))**2)**2
        else:
            speed_reward = 0
        reward += speed_reward * SPEED_MULTIPLE

        # Reward if less steps
        # ステップ数が少なければ報酬が発生
        # ここの内容を確認したい。（メモ）
        REWARD_PER_STEP_FOR_FASTEST_TIME = 1
        # seconds (time that is easily done by model)
        # #秒（モデルで簡単にできる時間）
        STANDARD_TIME = 100
        # seconds (best time of 1st place on the track)
        # #秒（コース1位のベストタイム）
        FASTEST_TIME = 52

        times_list = [row[3] for row in racing_track]
        projected_time = projected_time(
            self.first_racingpoint_index, closest_index, steps, times_list)
        try:
            steps_prediction = projected_time * 15 + 1
            reward_prediction = max(1e-3, (-REWARD_PER_STEP_FOR_FASTEST_TIME*(FASTEST_TIME) /
                                           (STANDARD_TIME-FASTEST_TIME))*(steps_prediction-(STANDARD_TIME*15+1)))
            steps_reward = min(REWARD_PER_STEP_FOR_FASTEST_TIME,
                               reward_prediction / steps_prediction)
        except:
            steps_reward = 0
        reward += steps_reward

        # Zero reward if obviously wrong direction (e.g. spin)
        # 明らかに間違った方向（例えばスピン）の場合は報酬ゼロ
        direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [x, y], heading)
        if direction_diff > 30:
            reward = 1e-3

        # Zero reward of obviously too slow
        # 明らかに遅すぎるという報酬はゼロ
        speed_diff_zero = optimals[2]-speed
        if speed_diff_zero > 0.5:
            reward = 1e-3

        ## Incentive for finishing the lap in less steps ##
        # should be adapted to track length and other rewards
        ## より少ない歩数で周回を終えるためのインセンティブ ##
        # トラックの長さや他の報酬に合わせるべき
        REWARD_FOR_FASTEST_TIME = 1500

        if progress == 100:
            finish_reward = max(1e-3, (-REWARD_FOR_FASTEST_TIME /
                                       (15*(STANDARD_TIME-FASTEST_TIME)))*(steps-STANDARD_TIME*15))
        else:
            finish_reward = 0
        reward += finish_reward

        ## Zero reward if off track ##
        ## 軌道を外れた場合の報酬はゼロ ##
        if all_wheels_on_track == False:
            reward = 1e-3

        ####################### VERBOSE #######################

        if self.verbose == True:
            print("Closest index: %i" % closest_index)
            print("Distance to racing line: %f" % dist)
            print("=== Distance reward (w/out multiple): %f ===" %
                  (distance_reward))
            print("Optimal speed: %f" % optimals[2])
            print("Speed difference: %f" % speed_diff)
            print("=== Speed reward (w/out multiple): %f ===" % speed_reward)
            print("Direction difference: %f" % direction_diff)
            print("Predicted time: %f" % projected_time)
            print("=== Steps reward: %f ===" % steps_reward)
            print("=== Finish reward: %f ===" % finish_reward)

        #################### RETURN REWARD ####################

        # Always return a float value
        return float(reward)


# パラメータ verbose=True を追加し、テスト用にノイズの多い出力を得る。
reward_object = Reward()  # add parameter verbose=True to get noisy output for testing


def reward_function(params):
    return reward_object.reward_function(params)
