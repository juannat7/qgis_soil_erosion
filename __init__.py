# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GR_SER
                                 A QGIS plugin
 This plugin assesses soil risk based on RUSLE model
                             -------------------
        begin                : 2018-06-11
        copyright            : (C) 2018 by Garuda Robotics
        email                : juan@garuda.io
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GR_SER class from file GR_SER.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .gr_ser import GR_SER
    return GR_SER(iface)
