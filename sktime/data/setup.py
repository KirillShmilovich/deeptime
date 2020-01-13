
def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration('data', parent_package, top_path)
    config.add_data_files(
        'data/double_well_discrete.npz',
    )

    return config
