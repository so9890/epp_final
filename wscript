#! python


import os

from collections import OrderedDict

# The project root directory and the build directory.
top = "."
out = "bld"


def set_project_paths(ctx):
    """Return a dictionary with project paths represented by Waf nodes."""

    pp = OrderedDict()
    pp["PROJECT_ROOT"] = "."
    pp["IN_DATA_CPI"] = "src/original_data/CPI_data"
    pp["IN_DATA_CEX"] = "src/original_data/CEX_data"
    pp["IN_DATA_GRAPH"] = "src/original_data/for_graph"
    pp["IN_DATA_CON"] = "src/original_data/Concordance"
    pp["IN_DATA_CEX_EXP"] = "src/data_management/CEX_shares"
    pp["IN_DATA_CEX_PERCN"] = "src/data_management/CEX_percentiles"
    pp["IN_DATA_MNGM_CPI"] = "src/data_management/CPI_management"
    pp["IN_DATA_FUNCTIONS"] = "src/data_management/data_functions"
    pp["LIBRARY"] = "src/library"
    pp["BLD"] = ""
    pp["OUT_DATA_CPI_CLEARED"] = f"{out}/out/data/CPI_prepared"
    pp["OUT_DATA_WEIGHTS_AND_EXPENDITURES"] = f"{out}/out/data/CEX_weights_and_expenditures"
    pp["OUT_DATA_CEX_CPI_MERGED"] = f"{out}/out/data/CEX_CPI_merged"
    pp["OUT_DATA_FINAL"] = f"{out}/out/data/final"
    pp["OUT_DATA_CPI_CON"] = f"{out}/out/data/CPI_and_CON"
    pp["OUT_DATA_CON_PREP"] = f"{out}/out/data/Concordance_prepared"
    pp["OUT_DATA_PERCENTILES"] =     f"{out}/out/data/CEX_percentiles"
    #pp["OUT_ANALYSIS"] = f"{out}/out/analysis"
    pp["OUT_FINAL"] = f"{out}/out/final"
    pp["OUT_FIGURES"] = f"{out}/out/figures"


    # Convert the directories into Waf nodes.
    for key, val in pp.items():
        if not key == "ADO":
            pp[key] = ctx.path.make_node(val)
        else:
            for adokey, adoval in val.items():
                pp[key][adokey] = ctx.path.make_node(adoval)
    return pp


def path_to(ctx, pp_key, *args):
    """Return the relative path to os.path.join(*args*) in the directory
    PROJECT_PATHS[pp_key] as seen from ctx.path (i.e. the directory of the
    current wscript).

    Use this to get the relative path---as needed by Waf---to a file in one
    of the directory trees defined in the PROJECT_PATHS dictionary above.

    We always pretend everything is in the source directory tree, Waf takes
    care of the correct placing of targets and sources.

    """

    # Implementation detail:
    #   We find the path to the directory where the file lives, so that
    #   we do not accidentally declare a node that does not exist.
    dir_path_in_tree = os.path.join(".", *args[:-1])
    # Find/declare the directory node. Use an alias to shorten the line.
    pp_key_fod = ctx.env.PROJECT_PATHS[pp_key].find_or_declare
    dir_node = pp_key_fod(dir_path_in_tree).get_src()
    # Get the relative path to the directory.
    path_to_dir = dir_node.path_from(ctx.path)
    # Return the relative path to the file.
    return os.path.join(path_to_dir, args[-1])


def configure(ctx):
    ctx.env.PYTHONPATH = os.getcwd()
    # Disable on a machine where security risks could arise
    ctx.env.PDFLATEXFLAGS = "-shell-escape"
    ctx.load("run_py_script")
    ctx.load("sphinx_build")
    ctx.load("write_project_headers")
    # ctx.find_program("dot")
    ctx.load("tex")



def build(ctx):
    ctx.env.PROJECT_PATHS = set_project_paths(ctx)
    ctx.path_to = path_to
    # Generate header file(s) with project paths in "bld" directory
    ctx(features="write_project_paths", target="project_paths.py")
    ctx.add_group()
    ctx.recurse("src")
