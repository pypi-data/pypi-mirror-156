import conifer
import datetime
import os
from sklearn.metrics import mean_absolute_error
import numpy as np
import logging
logger = logging.getLogger(__name__)

def autoQ(model, converter, X, output_dir='conifer_autoQ', atol=1e-2, rtol=1e-2):
  os.makedirs(output_dir)
  curr_dir = os.getcwd()
  os.chdir(output_dir)
  cfg = conifer.backends.cpp.auto_config()

  # establish baseline
  cfg['Precision'] = 'double'
  cfg['OutputDir'] = 'trial_0'

  cnf = conifer.model(model, converter, conifer.backends.cpp, cfg)
  cnf.compile()
  y_base = cnf.decision_function(X)

  iTrial = 1
  width = 25
  integer = 7 + 1
  good = True
  logger.info("Reducing Integer precision")
  while(good):
    last_model = cnf
    integer -= 1
    cfg = conifer.backends.cpp.auto_config()
    cfg['Precision'] = f'ap_fixed<{width},{integer},AP_RND_CONV,AP_SAT>'
    cfg['OutputDir'] = f'trial_{iTrial}'
    logger.info(f'Trial {iTrial} with precision {cfg["Precision"]}')
    cnf = conifer.model(model, converter, conifer.backends.cpp, cfg)
    cnf.compile()
    y_trial = cnf.decision_function(X)
    # an example metric
    abs_difference = np.abs(y_base - y_trial)
    rel_difference = abs_difference / np.abs(y_base)
    logger.info(f'Maximum absolute difference: {abs_difference.max():.5f}')
    logger.info(f'Maximum relative difference: {rel_difference.max():.5f}')
    good = good and np.all(abs_difference < atol) and np.all(rel_difference < rtol)
    iTrial += 1
  
  integer += 1
  good = True
  logger.info("Reducing width")
  while(good):
    last_model = cnf
    width -= 1
    cfg = conifer.backends.cpp.auto_config()
    cfg['Precision'] = f'ap_fixed<{width},{integer},AP_RND_CONV,AP_SAT>'
    cfg['OutputDir'] = f'trial_{iTrial}'
    logger.info(f'Trial {iTrial} with precision {cfg["Precision"]}')
    cnf = conifer.model(model, converter, conifer.backends.cpp, cfg)
    cnf.compile()
    y_trial = cnf.decision_function(X)
    # an example metric
    abs_difference = np.abs(y_base - y_trial)
    rel_difference = abs_difference / np.abs(y_base)
    logger.info(f'Maximum absolute difference: {abs_difference.max():.5f}')
    logger.info(f'Maximum relative difference: {rel_difference.max():.5f}')
    good = good and np.all(abs_difference < atol) and np.all(rel_difference < rtol)
    iTrial += 1
  
  width += 1
  cfg['Precision'] = f'ap_fixed<{width},{integer},AP_RND_CONV,AP_SAT>'
  #os.chdir(curr_dir)
  return last_model, cfg


def autoQ1(model, converter, X, metric, output_dir='conifer_autoQ', **metric_kwargs):
  os.makedirs(output_dir)
  curr_dir = os.getcwd()
  os.chdir(output_dir)
  cfg = conifer.backends.cpp.auto_config()

  # establish baseline
  cfg['Precision'] = 'double'
  cfg['OutputDir'] = 'trial_0'

  cnf = conifer.model(model, converter, conifer.backends.cpp, cfg)
  cnf.compile()
  y_base = cnf.decision_function(X)

  iTrial = 1
  width = 25
  integer = 7 + 1
  good = True
  logger.info("Reducing Integer precision")
  while(good):
    last_model = cnf
    integer -= 1
    cfg = conifer.backends.cpp.auto_config()
    cfg['Precision'] = f'ap_fixed<{width},{integer},AP_RND_CONV,AP_SAT>'
    cfg['OutputDir'] = f'trial_{iTrial}'
    logger.info(f'Trial {iTrial} with precision {cfg["Precision"]}')
    cnf = conifer.model(model, converter, conifer.backends.cpp, cfg)
    cnf.compile()
    y_trial = cnf.decision_function(X)
    # an example metric
    abs_difference = np.abs(y_base - y_trial)
    rel_difference = abs_difference / np.abs(y_base)
    logger.info(f'Maximum absolute difference: {abs_difference.max():.5f}')
    logger.info(f'Maximum relative difference: {rel_difference.max():.5f}')
    good = good and metric(y_base, y_trial, **metric_kwargs)
    iTrial += 1
  
  integer += 1
  good = True
  logger.info("Reducing width")
  while(good):
    last_model = cnf
    width -= 1
    cfg = conifer.backends.cpp.auto_config()
    cfg['Precision'] = f'ap_fixed<{width},{integer},AP_RND_CONV,AP_SAT>'
    cfg['OutputDir'] = f'trial_{iTrial}'
    logger.info(f'Trial {iTrial} with precision {cfg["Precision"]}')
    cnf = conifer.model(model, converter, conifer.backends.cpp, cfg)
    cnf.compile()
    y_trial = cnf.decision_function(X)
    # an example metric
    abs_difference = np.abs(y_base - y_trial)
    rel_difference = abs_difference / np.abs(y_base)
    logger.info(f'Maximum absolute difference: {abs_difference.max():.5f}')
    logger.info(f'Maximum relative difference: {rel_difference.max():.5f}')
    good = good and metric(y_base, y_trial, **metric_kwargs)
    iTrial += 1
  
  width += 1
  cfg['Precision'] = f'ap_fixed<{width},{integer},AP_RND_CONV,AP_SAT>'
  #os.chdir(curr_dir)
  return last_model, cfg