import numpy as np

from source.model import *
from unittest import TestCase

class TestCoordinateMap(TestCase):
    def setUp(self) -> None:
        self.object=CoordinateMap()
    def test_map_positionList_returnsPosition(self):
        position=[3.,4.]
        new_position=self.object.map(position)
        np.testing.assert_equal(new_position,position)
    def test_map_positionArray_returnsPosition(self):
        position = np.array([3., 4.])
        new_position = self.object.map(position)
        np.testing.assert_equal(new_position, position)
    def test_map_positionInt_raisesTypeError(self):
        position = 3
        self.assertRaises(TypeError,self.object.map,position)
    def test_map_positionStr_raisesTypeError(self):
        position = 'h'
        self.assertRaises(TypeError,self.object.map,position)
    def test_map_positionTuple_raisesTypeError(self):
        position = ()
        self.assertRaises(TypeError,self.object.map,position)
    def test_inverse_positionList_returnsPosition(self):
        position=[3.,4.]
        new_position=self.object.inverse(position)
        np.testing.assert_equal(new_position,position)
    def test_inverse_positionArray_returnsPosition(self):
        position = np.array([3., 4.])
        new_position = self.object.inverse(position)
        np.testing.assert_equal(new_position, position)
    def test_inverseAfterMap_positionArray_returnsOrigionalPosition(self):
        position = np.array([3., 4.])
        new_position = self.object.inverse(self.object.map(position))
        np.testing.assert_equal(new_position, position)

class TestLogCoordinateMap(TestCase):
    def setUp(self) -> None:
        self.object=LogCoordinateMap()
    def test_map_positionList_returnsPosition(self):
        position=[3.,4.]
        new_position=self.object.map(position)
        np.testing.assert_allclose(new_position, np.log(position))
    def test_map_positionArray_returnsPosition(self):
        position = np.array([3., 4.])
        new_position = self.object.map(position)
        np.testing.assert_allclose(new_position, np.log(position))
    def test_map_positionInt_raisesTypeError(self):
        position = 3
        self.assertRaises(TypeError,self.object.map,position)
    def test_map_positionStr_raisesTypeError(self):
        position = 'h'
        self.assertRaises(TypeError,self.object.map,position)
    def test_map_positionTuple_raisesTypeError(self):
        position = ()
        self.assertRaises(TypeError,self.object.map,position)
    def test_inverse_positionList_returnsPosition(self):
        position=[3.,4.]
        new_position=self.object.inverse(position)
        np.testing.assert_allclose(new_position, np.exp(position))
    def test_inverse_positionArray_returnsPosition(self):
        position = np.array([3., 4.])
        new_position = self.object.inverse(position)
        np.testing.assert_allclose(new_position, np.exp(position))
    def test_inverseAfterMap_positionArray_returnsOrigionalPosition(self):
        position = np.array([3., 4.])
        new_position = self.object.inverse(self.object.map(position))
        np.testing.assert_allclose(new_position, position)


class TestSigmoidCoordinateMap(TestCase):
    def setUp(self) -> None:
        self.object=SigmoidCoordinateMap()
    def test_map_positionList_returnsPosition(self):
        position=[3.,4.]
        new_position=self.object.map(position)
        np.testing.assert_allclose(new_position, self.object.amplitude/(1+np.exp(-np.array(position)*self.object.rate)))
    def test_map_positionArray_returnsPosition(self):
        position = np.array([3., 4.])
        new_position = self.object.map(position)
        np.testing.assert_allclose(new_position, self.object.amplitude/(1+np.exp(-np.array(position)*self.object.rate)))
    def test_map_positionInt_raisesTypeError(self):
        position = 3
        self.assertRaises(TypeError,self.object.map,position)
    def test_map_positionStr_raisesTypeError(self):
        position = 'h'
        self.assertRaises(TypeError,self.object.map,position)
    def test_map_positionTuple_raisesTypeError(self):
        position = ()
        self.assertRaises(TypeError,self.object.map,position)
    def test_inverse_positionList_returnsPosition(self):
        position=[3.,4.]
        new_position=self.object.inverse(position)
        np.testing.assert_allclose(new_position,-np.log(self.object.amplitude/np.array([3., 4.])-1)/self.object.rate)
    def test_inverse_positionArray_returnsPosition(self):
        position = np.array([3., 4.])
        new_position = self.object.inverse(position)
        np.testing.assert_allclose(new_position, -np.log(self.object.amplitude/np.array([3., 4.])-1)/self.object.rate)
    def test_inverseAfterMap_positionArray_returnsOrigionalPosition(self):
        position = np.array([3., 4.])
        new_position = self.object.inverse(self.object.map(position))
        np.testing.assert_allclose(new_position, position)


class TestModelParameters(TestCase):
    def setUp(self) -> None:
        self.object=ModelParameters()
    def test_init_empty_returnsParameters(self):
        object=ModelParameters()
    def test_init_list_returnsParameters(self):
        parameters=[1,1]
        object=ModelParameters(parameters)
        np.testing.assert_allclose(parameters, object.parameters)
    def test_init_listBounds_returnsParameters(self):
        parameters=[1,1]
        object=ModelParameters(parameters,bounds=[[0,5],[0, 5]])
        np.testing.assert_allclose(parameters,object.parameters)
    def test_init_listBoundsCoords_returnsParameters(self):
        parameters=[1,1]
        object=ModelParameters(parameters,bounds=[[0,5],[0, 5]],coordinates=SigmoidCoordinateMap())
        np.testing.assert_allclose(parameters, object.parameters)
    def test_numpy_list_returnsParameters(self):
        parameters=np.array([1,1])
        object=ModelParameters(parameters)
        np.testing.assert_allclose(parameters, object.parameters)
    def test_numpy_int_raisesTypeError(self):
        parameters=0
        self.assertRaises(TypeError,ModelParameters,parameters)
    def test_str_int_raisesTypeError(self):
        parameters="h"
        self.assertRaises(TypeError,ModelParameters,parameters)
    def test_setAll_list_works(self):
        parameters = [1, 1]
        self.object.setAll(parameters)
        np.testing.assert_allclose(parameters, self.object.parameters)
    def test_setAll_ndArray_works(self):
        parameters =np.array([1, 1])
        self.object.setAll(parameters)
        np.testing.assert_allclose(parameters, self.object.parameters)
    def test_setAll_ndArrayBounds_works(self):
        parameters =np.array([1, 1,3])
        self.object.setAll(parameters,bounds=[[0,.5],[0, .5],[0, .5]])
        np.testing.assert_allclose([.5, .5,.5], self.object.parameters)
    def test_set_ndArray_works(self):
        index=2
        parameter=1.
        self.object.set(index,parameter)
        np.testing.assert_allclose([0,0,1], self.object.parameters)

class TestModel(TestCase):
    def setUp(self) -> None:
        self.object=Model()
    def test_setAllParameters_list_returnsNone(self):
        parameters=[1.,2.]
        self.object.setAllParameters(parameters)
    def test_setAllParameters_numpy_arrayReturnsNone(self):
        parameters = np.array([1., 2.])
        self.object.setAllParameters(parameters)
    def test_setAllParameters_numpyBounds_arrayReturnsNone(self):
        parameters = np.array([1., 2.])
        self.object.setAllParameters(parameters,bounds=[[0,4],[0,5]])
    def test_setParameters_int_raisesTypeError(self):
        parameters=0.
        self.assertRaises(TypeError,self.object.setParameters,parameters)
    def test_setTime_array(self):
        time=np.linspace(0,5,5)
        self.object.setTime(time)
        np.testing.assert_allclose(time,self.object.time)
    def test_getTime(self):
        self.object.getTime()
    def test_setState_array(self):
        state=np.linspace(0,5,5)
        self.object.setState(state)
        np.testing.assert_allclose(state,self.object.state)
    def test_getState(self):
        self.object.getState()

class TestStateTrajectory(TestCase):
    def setUp(self) -> None:
        time = np.linspace(0, 5, 5)
        state = np.linspace(0, 5, 5)
        self.object = StateTrajectory(time, state)
    def test_init_empty_returnsTrajectory(self):
        object=StateTrajectory()
    def test_init_timestate_returnsTrajectory(self):
        time=np.linspace(0,5,5)
        state = np.linspace(0, 5, 5)
        object=StateTrajectory(time,state)
    def test_init_timestate_raisesValueError(self):
        time=np.linspace(0,5,5)
        state = np.linspace(0, 5, 5)
        self.assertRaises(ValueError,StateTrajectory,(state))
    def test_getTime_empty_returnsTime(self):
        time=self.object.getTime()
        np.testing.assert_allclose(np.linspace(0, 5, 5), time)
    def test_setTime_empty_returnsNone(self):
        time = np.linspace(0, 5, 5)
        self.object.setTime(time)
        np.testing.assert_allclose(self.object.time, time)
    def test_getState_empty_returnsTime(self):
        state=self.object.getState()
        np.testing.assert_allclose(np.linspace(0, 5, 5),state)
    def test_setState_empty_returnsNone(self):
        state= np.linspace(0, 5, 5)
        self.object.setState(state)
        np.testing.assert_allclose(self.object.state, state)

class TestTrajectories(TestCase):
    def setUp(self) -> None:
        self.object=StateTrajectories()
    def test_add_trajecgtory(self):
        trajectory=StateTrajectory()
        self.object.add(trajectory)
    def test_add_list_raisesTypeError(self):
        trajectory=[]
        self.assertRaises(TypeError,self.object.add,trajectory)

class TestModelLibrary(TestCase):
    def setUp(self) -> None:
        self.object=ModelLibrary()
    def test_get_empty_birthDecay_returnsModel(self):
        model=self.object.get('birthDecay')
        self.assertIsInstance(model,Model)

class TestSolverODE(TestCase):
    def setUp(self) -> None:
        self.object=SolverODE()
        self.lib=ModelLibrary()
    def test_run_model_returnsTrajectory(self):
        model = self.lib.get('birthDecay')
        trajectory=self.object.run(model)
        self.assertIsInstance(trajectory,StateTrajectory)
    def test_run_model2D_returnsTrajectory(self):
        model = self.lib.get('birthDecay2D')
        trajectory = self.object.run(model)
        self.assertIsInstance(trajectory, StateTrajectory)

class TestSolverSSA(TestCase):
    def setUp(self) -> None:
        self.object=SolverSSA()
        self.lib=ModelLibrary()
    def test_run_model_returnsTrajectory(self):
        model = self.lib.get('birthDecay')
        trajectories = self.object.run(model)
    def test_run_modelnumber_returnsTrajectory(self):
        model = self.lib.get('birthDecay')
        numRuns=5
        trajectories = self.object.run(model,numRuns)
    def test_run_model2D_returnsTrajectory(self):
        model = self.lib.get('birthDecay2D')
        trajectories = self.object.run(model)
    def test_run_modelnumber2D_returnsTrajectory(self):
        model = self.lib.get('birthDecay2D')
        numRuns=5
        trajectories = self.object.run(model,numRuns)

class TestSolverFSP(TestCase):
    def setUp(self) -> None:
        self.object=SolverFSP([5,5])
        self.lib=ModelLibrary()
    def test_run_model1D_returnsTrajectory(self):
        object = SolverFSP([5])
        model = self.lib.get('birthDecay')
        trajectory = object.run(model)
    def test_run_model2D_returnsTrajectory(self):
        object = SolverFSP([5, 5])
        model = self.lib.get('birthDecay2D')
        trajectory = object.run(model)