import pandas as pd
import numpy as np


class CorrectBias(object):
    def __init__(self, taper_width, npv_observations):
        self.taper_width = taper_width
        self.sampled_controls_loc, self.sampled_controls_beta = self.get_data(npv_observations)
        self.est_mean_alpha = np.mean(self.sampled_controls_beta)

    def get_data(self, obs_data):
        """
        obs_data: col_1 = random control;
                  col_2 = npv obtained from a single model realization (random controls applied to different realizations)
                  col_3 = npv obtained from mean model

        """

        # get a list of sampled controls from .csv files
        action_name = obs_data["control"]
        action_list = list()
        for action_index in range(0, action_name.size):
            temp_seq = action_name[action_index]
            temp_seq = temp_seq[1:-1].split(",")
            temp_seq = [it.replace(" ", "")[1:-1] for it in temp_seq]
            action_list.append(temp_seq)

        # compute partial correction factor beta f
        sampled_controls_beta = obs_data["individual_realization"].to_numpy() / obs_data["mean_model"].to_numpy()

        # compute well-position based location for all sampled random drilling sequences
        sampled_controls_loc = self.get_loc_multiple(action_list)

        return sampled_controls_loc, sampled_controls_beta

    def get_loc_multiple(self, action_list):
        ref_order = ['OP_1', 'OP_2', 'OP_3', 'OP_4', 'OP_5', 'WI_1', 'WI_2', 'WI_3']
        all_locations = np.zeros((len(action_list), 8))

        for action_index in range(0, len(action_list)):

            temp_action = action_list[action_index]
            if temp_action[0] == '':
                temp_order = [1] * len(ref_order)
                all_locations[action_index, :] = temp_order
            else:
                temp_order = [len(temp_action) + 1] * len(ref_order)
                temp_order = np.array(temp_order)
                upd_order = list(range(1, len(temp_action) + 1))
                upd_order = np.array(upd_order)
                order_index = []

                for j in range(0, len(temp_action)):
                    get_index = ref_order.index(temp_action[j])
                    order_index.append(get_index)

                order_index = np.array(order_index)
                temp_order[order_index] = upd_order
                temp_order = np.reshape(temp_order, (1, 8))
                all_locations[action_index, :] = temp_order

        return all_locations

    # compute location for a set of random drilling sequences
    def get_loc_single(self, seq_action):
        """
        # permutation encodings:
        ref., ['OP_1', 'OP_2', 'OP_3', 'OP_4', 'OP_5', 'WI_1', 'WI_2', 'WI_3'] -> [1 , 2 , 3 , 4, 5, 6, 7, 8];
             if input = ['WI_3', 'OP_5', 'OP_3', 'OP_1', 'OP_4', 'WI_2', 'OP_2', 'WI_1']
             output =  [4 , 7 , 3 , 5, 2, 8, 6, 1];
        """
        ref_order = ['OP_1', 'OP_2', 'OP_3', 'OP_4', 'OP_5', 'WI_1', 'WI_2', 'WI_3']
        loc_seq = np.zeros((1, 8))

        temp_action = seq_action
        temp_order = [len(temp_action) + 1] * len(ref_order)
        temp_order = np.array(temp_order)
        upd_order = list(range(1, len(temp_action) + 1))
        upd_order = np.array(upd_order)

        order_index = []
        if temp_action == []:
            temp_order = [1] * len(ref_order)
            loc_seq[0, :] = temp_order
        else:

            for j in range(0, len(temp_action)):
                get_index = ref_order.index(temp_action[j])
                order_index.append(get_index)

            order_index = np.array(order_index)
            temp_order[order_index] = upd_order
            temp_order = np.reshape(temp_order, (1, 8))
            loc_seq[0, :] = temp_order

        return loc_seq

    #
    def gaspari_cohn(self, distance_values):
        distance_range = self.taper_width
        weight_values = np.zeros(distance_values.shape[0], )

        z = distance_values / distance_range

        index_1 = np.where(z <= 1)[0]
        index_2 = np.where(z <= 2)[0]
        index_12 = np.setdiff1d(index_2, index_1)

        weight_values[index_1] = - (z[index_1] ** 5) / 4 + (z[index_1] ** 4) / 2 + (z[index_1] ** 3) * (5 / 8) - (
                z[index_1] ** 2) * (5 / 3) + 1
        weight_values[index_12] = (z[index_12] ** 5) / 12 - (z[index_12] ** 4) / 2 + (z[index_12] ** 3) * (5 / 8) + (
                z[index_12] ** 2) * (5 / 3) - z[index_12] * 5 + 4 - (z[index_12] ** -1) * (2 / 3)

        return weight_values

    def cal_distance(self, est_control_loc):
        """
        ref_seq_loc: location for estimation point (
        return: a list of distance between estimation point
        """

        # sampled_control_loc = self.selected_seq_loc

        # compute distance between estimation point and all sampled control
        dist_each = np.abs(self.sampled_controls_loc - est_control_loc)
        manhattan_distance = np.sum(dist_each, axis=1)

        return manhattan_distance

    # compute local estimate of bias-correction factor alpha
    def cal_alpha_loc(self, weight_values):
        sum_weight = np.sum(weight_values, axis=0)
        n_eff = np.sum(weight_values) ** 2 / np.sum(weight_values ** 2)
        est_alpha_loc = np.sum(weight_values * self.sampled_controls_beta) / sum_weight

        return est_alpha_loc, n_eff

    # compute local estimate of expected value
    def local_estimate(self, seq_action, initial_approx):

        # permutation encodings: eg.,  [W1 , W2 , W3 , W4 ] -> [1 , 2 , 3 , 4]; [W3 , W1 , W4 , W2 ]-> [2, 4, 1, 3]
        seq_loc = self.get_loc_single(seq_action)

        # compute manhattan distance between estimation point(current control) and sampled controls
        seq_distance = self.cal_distance(seq_loc)

        # compute distance-based weights
        weights = self.gaspari_cohn(seq_distance)

        # compute local estimate of alpha & effective sample size (n_eff)
        # (for distance-based localization, n_eff is not necessary )
        est_alpha_loc, est_n_eff = self.cal_alpha_loc(weights)

        # compute local estimation of expected NPV
        expected_value_loc = est_alpha_loc * initial_approx

        return expected_value_loc,  est_alpha_loc, est_n_eff

    # if varaince of alpha / beta is known  - > regularized localization
    def regularized_estimate(self, seq_action, initial_approx, var_alpha, var_beta):

        # compute local estimation of expected value, bias-correction factor and effective sample size
        expected_value_loc, alpha_loc, n_eff = self.local_estimate(seq_action, initial_approx)

        # compute regularized estimate of expected value
        gamma = 1 + var_beta / (var_alpha * n_eff)
        expected_value_reg = (expected_value_loc + gamma * self.est_mean_alpha) / (1 + gamma)

        return expected_value_reg


if __name__ == '__main__':
    """
    Bias-correction method - computing an approximation of expected value
    Main idea:  (Paper: https://link.springer.com/article/10.1007/s10596-020-10017-y)
    E(J(x_j,m)) ≈  \alpha * J(x_j, m_ref) (eg., m_ref = \bar m)
    \alpha(x_j) = G(\beta_{1},\beta_{2}, ... ,\beta_n , x_j).
    alpha: bias-correction factor
    beta: partial correction factor:\beta_{ij} =\beta(\mathbf{x_i,m_j,\bar m}) =  \frac{J(\mathbf{x_i,m_j})}{J(\mathbf{x_i, \bar m})}.

    Three possible ways to estimate bias correction factor \alpha
    1. pure distance-based localization
    2. regularized localization
    3. Covariance-based optimal weights
    (The latter two require additional information about the correction factor (variance of bias-correction factor),
    
    """

    # npv from single realization/ mean model (100 random drilling sequences)
    # col_1 = drilling sequences (x_i), col_2 = J(x_i,m_i), col_3 =J(x_i,\bar m)
    npv_obs = pd.read_csv("npv_obs_example.csv")

    # current_control: x_j (eg., specific drilling sequence)
    current_control = ['WI_3', 'OP_5', 'OP_3', 'OP_1', 'OP_4', 'WI_2', 'OP_2', 'WI_1']

    # initial approximation obtained from reference model (mean model): J(x_j, \bar m)
    npv_mean_model = 6870454326

    # depend on application / distance measure (for reference, the maximum Manhattan distance between 8 wells is 32)
    taper_length = 25

    # estimate expected value using bias-corrected mean model (eg., distance-based localization)
    approx_update = CorrectBias(taper_length, npv_obs)
    expected_NPV_loc, alpha_loc, n_eff = approx_update.local_estimate(current_control, npv_mean_model)

    print("---------------------------------------------------------------------------------------------")
    print("Estimation Point:", current_control, "\nNPV from mean model:", npv_mean_model)

    print("------------------------  Bias-correction method (distance-based localization) ---------------")
    print("Approximation of expected NPV:", expected_NPV_loc,
          "\nEstimation of bias correction factor (alpha):", alpha_loc,
          "\nEnsemble size / number of sampled controls:", 100)





