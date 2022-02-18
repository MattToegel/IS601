from Car import Car
import pytest

speed_data = [{
    "speed_in": 50,
    "speed_out": 45
}]


@pytest.mark.parametrize("speed_brake", speed_data)
def test_car_brake(my_car, speed_brake):
    my_car.speed = speed_brake["speed_in"]
    my_car.brake()
    assert my_car.speed == speed_brake["speed_out"]


"""def test_car_brake_neg(my_car):

    my_car.brake()
    assert my_car.speed == 50"""


@pytest.mark.parametrize("speed_accelerate", speed_data)
def test_car_accel(my_car, speed_accelerate):
    my_car.speed = speed_accelerate["speed_in"]
    my_car.accelerate()
    assert my_car.speed == speed_accelerate["speed_out"]


@pytest.fixture
def my_car():
    return Car(50)
