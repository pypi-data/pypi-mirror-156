"""all code concerning the status of lemmings jobs"""

import os
import numpy as np
from prettytable import PrettyTable
from lemmings.base.database import Database

PROGRESS_VAR = "completion"

def get_current_status(dataBase, keys=None, with_progress=False):
    """
    Function returning the current status of the simulation.
    """
    # keys : is an option that could allow a future control of what to output
    #           but needs to be developed if eventually needed
    status_string = []
    # NOTE: consider using logging package of python

    try:
        db_content = dataBase._database
    except FileNotFoundError as excep:
        status_string.append("LemmingsError: " + excep)
        return status_string

    chain_name = dataBase.latest_chain_name
    if chain_name is None:
        raise ValueError(
            "No chain found. Check database.json file in your current directory ..."
        )

    # --Check first if the database is the main one of a parallel run---#
    parallel_run = False
    try:
        (par_dict,) = dataBase.get_current_loop_val("parallel_runs")
        parallel_run = True
    except KeyError:
        pass

    if parallel_run:
        return parallel_status(with_progress, par_dict)


    def _handle_first_loop(loop, loop_num, keys):
        """Function rendering the lemmings status in case of a first loop
        of a chain of a first loop after a --restart
        """
        value_list = []

        for key in keys:
            if key in loop:
                if key in ["solut_path"]:
                    tmp_path = loop[key].split("/")[0]
                    if tmp_path == ".":
                        tmp_path = "./"
                    value_list.append(tmp_path)
                elif key in ["job_id", "pjob_id"]:
                    value_list.append(loop[key])
                else:
                    value_list.append("Submitted")
            else:
                value_list.append("Submitted")
        value_list = [str(ii)] + value_list

        return value_list

    status_string.append("Status for chain %s " % (chain_name))

    names_keys = keys
    if keys is None:
        keys = ["solut_path", "condition_reached"]
        keys.append(PROGRESS_VAR)
        keys.extend(["end_cpu_time", "job_id", "pjob_id"])

        names_keys = [
            "Solution path",
            "Job end status",
            "progress",
            "CPU time (h)",
            "job ID",
            "pjob ID",
        ]

    end_message = None

    match_cond_reached_keys = {
        "True": "ended, finalized",
        "False": "ended, continue",
        "None": "ended, crashed",
    }
    table = PrettyTable()
    for ii, loop in enumerate(db_content[chain_name]):
        value_list = []

        # TODO: check that correctly done as we check the current loop -> latest active
        # Separate handling of first loop situation
        if dataBase.get_current_loop_val("loop_count") == 1:
            if not "condition_reached" in loop:
                # in case condition_reached is present, we went to post_job already
                # then the handling should be the normal one
                value_list = _handle_first_loop(loop, ii, keys)
                table.field_names = ["Loop"] + names_keys
                table.add_row(value_list)

                if loop["end_message"] is not None:
                    end_message = customise_end_message(
                        dataBase, ii, loop["end_message"]
                    )
                break

            if not "end_cpu_time" in loop:
                # case first loop is running
                value_list = _handle_first_loop(loop, ii, keys)
                table.field_names = ["Loop"] + names_keys
                table.add_row(value_list)
                break

        if "restart" in loop:
            if loop["restart"]:
                end_message = None  # we reinit the end_message as loop restarted
                value_list = ["restart"] + ["-----"] * len(keys)
                table.add_row(value_list)
                value_list = []  # reinit value_list
                if not "end_cpu_time" in loop:
                    value_list = _handle_first_loop(loop, ii, keys)

                    table.field_names = ["Loop"] + names_keys
                    table.add_row(value_list)
                    if loop["end_message"] is not None:
                        end_message = customise_end_message(
                            dataBase, ii, loop["end_message"]
                        )
                    break

        if not "solut_path" in loop and not "job_id" in loop:
            # JJ: this case won't happen any more I believe
            # print(database.count, ii)
            # if ii == database.count:
            # if 'job_id' in loop:
            #     continue
            if loop["end_message"] is not None:
                end_message = customise_end_message(dataBase, ii, loop["end_message"])
            break
        else:
            for key in keys:
                if key in loop:
                    if key in [PROGRESS_VAR]:
                        tmp_key = np.round(loop[key], 4)
                        value_list.append(tmp_key)
                    elif key in ["end_cpu_time"]:
                        value_list.append(np.round(loop[key], 3))
                    elif key in ["solut_path"]:
                        tmp_path = loop[key].split("/")[0]
                        if tmp_path == "." and tmp_path is not None:
                            tmp_path = "./"
                        value_list.append(tmp_path)
                    elif key in ["condition_reached"]:
                        tmp_key = loop[key]
                        value_list.append(match_cond_reached_keys[str(tmp_key)])
                    else:
                        value_list.append(loop[key])
                else:
                    if (
                        "condition_reached" not in loop
                    ):  # will only be added in post_job part
                        value_list.append("Submitted")
                    elif key in [PROGRESS_VAR]:
                        value_list.append("NA")
                    elif "solut_path" not in loop:
                        try:
                            tmp_path = dataBase.get_first_loop_val("solut_path").split(
                                "/"
                            )[0]
                            if tmp_path == "." and tmp_path is not None:
                                tmp_path = "./"
                            value_list.append(tmp_path)
                        except KeyError as excep:
                            # assume it's in the main directory, perhaps consider 'NA' instead
                            value_list.append("./")
                            continue
                    else:
                        value_list.append("NA")
            value_list = [str(ii)] + value_list
            table.field_names = ["Loop"] + names_keys
            table.add_row(value_list)

            try:
                if loop["end_message"] is not None:
                    end_message = customise_end_message(
                        dataBase, ii, loop["end_message"]
                    )
            except KeyError:  # case when post_job still has to run and add end_message to database
                pass

    status_string.append(table)
    if end_message is not None:
        status_string.append("Lemmings ended: " + end_message)

    return status_string


def parallel_status(with_progress, par_dict):
    status_string = []
    table = PrettyTable()
    
    symbol = {
        "start": "S",
        "wait": "W",
        "end": "F",
        "error": "E",
        "kill": "K",
    }
    if not with_progress:
        table.field_names = ["Workflow number", "Status"]
        table.add_rows(
            [(key, symbol.get(val, "?")) for key, val in par_dict.items()]
        )
    else:
        # case with progress variable
        table.field_names = ["Workflow number", "Status", "Progress"]
        _string = [
            (key, symbol.get(val, "?"), "NA") for key, val in par_dict.items()
        ]
        main_dir = os.getcwd()
        for ii, keys in enumerate(_string):
            if keys[1] in ["W"]:
                break
            os.chdir(keys[0])
            tmp_dataBase = Database()
            try:
                tmp_progress = tmp_dataBase.get_current_loop_val(PROGRESS_VAR)
            except KeyError:
                # case when progress var not yet added in current loop
                # we will then instead use the previous loop
                if tmp_dataBase.get_current_loop_val("loop_count") == 1:
                    break
                tmp_progress = tmp_dataBase.get_previous_loop_val(PROGRESS_VAR)
                
            if isinstance(tmp_progress, float):
                tmp_progress = np.round(tmp_progress, 5)
            _string[ii] = (_string[ii][0], _string[ii][1], tmp_progress)
            os.chdir(main_dir)
        table.add_rows(_string)
    status_string.append(
        "S: Submitted, F: Finished, W: Wait, E: Error, K: Killed"
    )
    status_string.append(table)
    
    return status_string

def customise_end_message(dataBase, loop_num, end_msg):
    """Function handling the end message output shown in 'lemmings status'

    Input:
        :database: database class object
        :loop_num: int, number of the loop calling this functionality
    Output:
        :end_message: str, ouput to be provided
    """

    if not isinstance(loop_num, int):
        loop_num = int(loop_num)

    end_message = "\n  Latest loop = %1d \n" % loop_num

    try:
        # Starts counting at 1!!
        end_message += [
            "  Latest job and pjob IDs = "
            + dataBase.get_loop_val("job_id", (loop_num + 1))
            + " and "
            + dataBase.get_loop_val("pjob_id", (loop_num + 1))
        ][0]
    except KeyError:
        pass

    end_message += "\n  Final status: " + end_msg
    end_message = "# " + "\n # ".join(end_message.splitlines())
    return end_message
