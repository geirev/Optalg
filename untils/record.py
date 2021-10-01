# Copyright (c) 2018-2021 NORCE, All Rights Reserved. DIGIRES (PhD Wang)
import xlwt


class Record(object):
    def __init__(self, drillingtime, index=None):
        self.drillingtime = drillingtime
        self.index = index

    def get_action(self, schedule):
        action = ""
        for index in range(len(schedule) - 1):
            if schedule[index][1] == self.drillingtime \
                    and schedule[index + 1][1] == self.drillingtime:
                action += "," + schedule[index][0]
        if schedule[-1][1] == self.drillingtime:
            action += "," + schedule[-1][0]
        action = action[1:] if action != '' else 'root'
        return action

    def write_format(self, node):
        action = self.get_action(node['schedule'])
        print(
            '''[action = %s] : {
    [schedule = %s]
    [g = %s]
    [hr = %s]
    [hs = %s]
    [total_g = %s]
    [initial_hr = %s]
    [total_ghr = %s]
    [initial_hs = %s]
    [original_npv = %s]
    [adjust_values = %s]
    [check_value = %s]
    [ranked_producers = %s]
    [ranked_injectors = %s]   
    [next_actions = %s]
}''' % (action,node['schedule'], node['g'], node['hr'], node['hs'],  node['total_g'], node['initial_hr'],
                node['total_ghr'], node['initial_hs'], node['original_npv'],node['adjust_values'], node['check_value'], node['ranked_producers'],node['ranked_injectors'],
                 node['next_actions']))
        print()

    def write_to_command(self, all_nodes, open_table, close_table, total_table, removed_nodes):
        length_step = len(open_table)
        print(len(open_table))
        print(len(close_table))
        for step in range(length_step):
            print('{0:*^100}'.format(' Step %d ' % step))
            print('OPEN => ')
            for index in open_table[step]:
                node = all_nodes[index]
                self.write_format(node)
            print('\nCLOSE => ')
            for index in close_table[step]:
                node = all_nodes[index]
                self.write_format(node)
        print('\n{0:*^100}'.format(' Total '))
        for step, item in enumerate(total_table):
            print('{0:*^100}'.format(' New successor nodes at step %d ' % step))
            for index in item:
                node = all_nodes[index]
                self.write_format(node)
        print('\n{0:*^100}'.format(' Removed Nodes '))
        for item in removed_nodes:
            node = all_nodes[item]
            self.write_format(node)

    def write_to_file(self, all_nodes, total_table, close_table, removed_nodes, path):
        workbook = xlwt.Workbook(encoding='utf-8')

        keys = ['g', 'hr', 'hs', 'total_g', 'initial_hr', 'total_ghr', 'initial_hs',
                'original_npv', 'adjust_values','check_value','ranked_producers','ranked_injectors','next_actions']

        worksheet = workbook.add_sheet('tol_values', cell_overwrite_ok=True)
        row = 0
        worksheet.write(row, 0, 'action')
        for col, item in enumerate(keys):
            worksheet.write(row, col + 1, item)
        row += 1
        for tbl in total_table:
            for index in tbl:
                node = all_nodes[index]
                action = self.get_action(node['schedule'])
                worksheet.write(row, 0, action)
                for col, key in enumerate(keys):
                    worksheet.write(row, col + 1, str(node[key]))
                row += 1

        worksheet = workbook.add_sheet('last_close', cell_overwrite_ok=True)
        row = 0
        worksheet.write(row, 0, "action")
        for col, item in enumerate(keys):
            worksheet.write(row, col + 1, item)
        row += 1
        for index in close_table:
            node = all_nodes[index]
            action = self.get_action(node['schedule'])
            worksheet.write(row, 0, action)
            for col, key in enumerate(keys):
                worksheet.write(row, col + 1, str(node[key]))
            row += 1

        worksheet = workbook.add_sheet('removed_nodes', cell_overwrite_ok=True)
        row = 0
        worksheet.write(row, 0, "action")
        for col, item in enumerate(keys):
            worksheet.write(row, col + 1, item)
        row += 1
        for index in removed_nodes:
            node = all_nodes[index]
            action = self.get_action(node['schedule'])
            worksheet.write(row, 0, action)
            for col, key in enumerate(keys):
                worksheet.write(row, col + 1, str(node[key]))
            row += 1

        file_name = "/sol_" + self.index + ".xls"
        workbook.save("./results/deterministic_solution"+ file_name)
        #workbook.save(path + file_name)
