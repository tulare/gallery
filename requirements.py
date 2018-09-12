# -*- encoding: utf-8 -*-
from __future__ import print_function

import sys
import os

from pkg_resources import (
    DistributionNotFound,
    Requirement, Environment,
    require, get_distribution,
    working_set
)

ROOT_FOLDER = os.path.dirname(os.path.realpath(__file__))

with open(ROOT_FOLDER + '/requirements.txt') as fp :
    requirements = [ req.strip() for req in fp.readlines() ]

environment = Environment([])

for requirement in requirements :
    try :
        # distrib disponible directement ?
        distrib = get_distribution(requirement)
        environment.add(distrib)

    except DistributionNotFound :
        # meilleur candidat pour cette distrib aux emplacements suivants
        environment.scan([
            ROOT_FOLDER + '/eggs',
            'D:/devel/00modules/' + requirement
        ])
        distrib = environment.best_match(
            Requirement.parse(requirement),
            working_set
        )
        if distrib is not None :
            working_set.add(distrib)

    print(require(requirement), file=sys.stderr)
