import numpy as np
import data.utils as u


class Data():
    """
    Storage class specific to ground truth data generated by CARLA simulator.
    """
    
    # constructor 
    def __init__(self, 
                 t=np.array([None]), 
                 p=np.array([None]), 
                 v=np.array([None]),
                 a=np.array([None]),
                 w=np.array([None]), 
                 r=np.array([None]), 
                 alpha=np.array([None]), 
                 do_diff = False):
        """
        :param t: Timestamps [s]
        
        :param p: Position [m]
        :param v: Velocity [m/s]
        :param a: Acceleration [m/s^2]
        
        :param r: Orientation [rad]
        :param w: Ang. Velocity [rad/s]
        :param alpha: Ang. Acceleration [rad/s^2]

        :param diff: Flag - generate velocities and accelerations by differentiating
        """
        # initialize value
        self._p_init = p
        self._v_init = v
        self._a_init = a
        
        self._r_init = r
        self._w_init = w
        self._alpha_init = alpha
        

        # 
        self._t = t
        
        self._p = p
        self._v = v
        self._a = a
        
        self._r = r
        self._w = w
        self._alpha = alpha
        
        self.do_diff = do_diff

    def reset(self):
        """
        Resets all data back to initial (ground truth) positions and orientations.
        """
        self._p = self._p_init
        self._r = self._r_init
        self._v = self._v_init
        self._w = self._w_init
        self._a = self._a_init
        self._alpha = self._alpha_init
    
    # Position [m]
    @property
    def p(self):
        if self._p.any():
            return self._p
        raise ValueError('No position data available.')

    @p.setter
    def p(self, value):
        self._p = value
    
    # Velocity [m/s]
    @property
    def v(self):
        if self._v.any():
            return self._v
        elif self.do_diff:
            self._v = np.array(u.diff(self.p, self._t))
            return self._v
        raise ValueError('No velocity data available')

    @v.setter
    def v(self, value):
        self._v = value
    
    # Acceleration [m/s^2]
    @property
    def a(self):
        if self._a.any():
            return self._a
        elif self.do_diff:
            self._a = np.array(u.diff(self.v, self._t))
            return self._a
        raise ValueError('No acceleration data available')

    @a.setter
    def a(self, value):
        self._a = value

    # Orientation [rad]
    @property
    def r(self):
        if self._r.any():
            return self._r
        raise ValueError('No orientation data available.')

    @r.setter
    def r(self, value):
        # Active transform convention - roll applied first, then
        # pitch and then yaw.
        self._r = value
        
    # Ang. Velocity [rad/s]
    @property
    def w(self):
        if self._w.any():
            return self._w
        elif self.do_diff:
            # First determine \dot{Theta} - the rates of change of the
            # Euler angles...
            self._w = np.array(u.diff(self.r, self._t))

            # Now convert to angular velocities *in the vehicle (IMU) frame*.
            for i in (range(len(self._w))):
                # Referencing _r ... must be set before a call to w(self).
                self._w[i, :] = u.to_angular_rates(self.r[i, :], self._w[i, :])
            return self._w
        raise ValueError('No angular velocity data available')

    @w.setter
    def w(self, value):
        self._w = value
        
    # Ang. Acceleration [rad/s^2] 
    @property
    def alpha(self):
        if self._alpha.any():
            return self._alpha
        elif self.do_diff:
            self._alpha = np.array(u.diff(self.w, self._t))
            return self._alpha
        raise ValueError('No angular acceleration data available')

    @alpha.setter
    def alpha(self, value):
        self._alpha = value

    def transform(self, T = np.array([[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1, 0],[0, 0, 0, 1]]), side = "right"):
        if side == "right":
            p, r = u.transform_data_right(self.p, self.r, T)
        else:
            p, r = u.transform_data_left(self.p, self.r, T)
        
        return Data(self._t, p, r, do_diff = True)

    def slice(self, s = 0, e = 0):
        """" Slice all data from s to e."""
        self.p = self.p[s:e]
        self.v = self.v[s:e]
        self.a = self.a[s:e]
        self.r = self.r[s:e]
        self.w = self.w[s:e]
        self.alpha = self.alpha[s:e]