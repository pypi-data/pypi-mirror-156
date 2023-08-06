# gen_array

import numpy as np


def RK4_Propagator(start: float, end: float, N: int, u0: np.ndarray) -> np.ndarray:
  """Propagating orbit with RK4.

  Parameters
  ----------
  start : float
    Propagation start time in julian seconds.
  end : float
    Propagation end time in julian seconds.
  N : int
    Number of time steps.
  u0 : np.ndarray
    Array of shape (6,) containing the initial solution.
  
  Returns
  -------
  np.ndarray
    Propagated solution.
  """

  # Initialize values
  GM = 3.986e14
  u = np.zeros((6, N+1))
  h = (end-start)/N

  u[0, 0] = u0[0]
  u[1, 0] = u0[1]
  u[2, 0] = u0[2]
  u[3, 0] = u0[3]
  u[4, 0] = u0[4]
  u[5, 0] = u0[5]


  # Run the loop to generate the data values

  for n in range(N): 
    
    # RK4 and Orbit calculations

    mag_r = np.linalg.norm(u[:3, n])

    k1 = np.array([
                    u[3, n],
                    u[4, n],
                    u[5, n],
                    (-GM/mag_r**3) * u[0, n],
                    (-GM/mag_r**3) * u[1, n],
                    (-GM/mag_r**3) * u[2, n]])
  
    temp_u_mid = u[:, n] + h / 2 * k1
    mag_r = np.linalg.norm(temp_u_mid[:3])

    k2 = np.array([
                    temp_u_mid[3],
                    temp_u_mid[4],
                    temp_u_mid[5],
                    (-GM/mag_r**3) * temp_u_mid[0],
                    (-GM/mag_r**3) * temp_u_mid[1],
                    (-GM/mag_r**3) * temp_u_mid[2]])
  
  
    temp_u_mid = u[:, n] + h / 2 * k2
    mag_r = np.linalg.norm(temp_u_mid[:3])

    k3 = np.array([
                    temp_u_mid[3],
                    temp_u_mid[4],
                    temp_u_mid[5],
                    (-GM/mag_r**3) * temp_u_mid[0],
                    (-GM/mag_r**3) * temp_u_mid[1],
                    (-GM/mag_r**3) * temp_u_mid[2]])
  
    temp_u_mid = u[:, n] + h * k3
    mag_r = np.linalg.norm(temp_u_mid[:3])

    k4 = np.array([
                    temp_u_mid[3],
                    temp_u_mid[4],
                    temp_u_mid[5],
                    (-GM/mag_r**3) * temp_u_mid[0],
                    (-GM/mag_r**3) * temp_u_mid[1],
                    (-GM/mag_r**3) * temp_u_mid[2]])
  
  
    u[:, n+1] = u[:, n] + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
  
  return u