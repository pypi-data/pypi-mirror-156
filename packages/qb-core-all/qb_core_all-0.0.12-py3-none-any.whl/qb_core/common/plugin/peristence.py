import importlib


class PersistencePluginManager:
    persistence_obj_dict = {}

    @classmethod
    def initialize(cls, persistence_interface_module_name, persistence_impl_module_name):
        """
        examples
        (persistence_interface_module_name="cook_persistence_interface", module_name="qb_core.rats_pkg.cook.cook_persistence_core")
        (persistence_interface_module_name="cook_persistence_interface", module_name="cook.cook_persistence_dynamodb")
        :param persistence_interface_module_name:
        :param persistence_impl_module_name:
        :return:
        """
        module = importlib.import_module(persistence_impl_module_name)
        cls.persistence_obj_dict[persistence_interface_module_name] = module
        #
        # if persistence_interface_module_name == "core":
        #     module = importlib.import_module("qb_core.rats_pkg.cook.cook_persistence_core")
        #     cls.persistence_obj = module.get_implementation()
        # else:
        #     module = importlib.import_module("qb_core.rats_pkg.cook.cook_persistence_core")
        #     cls.persistence_obj = module.get_implementation()

    @classmethod
    def get_persistence_implementation(cls, persistence_interface_module_name):
        # return cls.persistence_obj
        module = cls.persistence_obj_dict.get(persistence_interface_module_name)
        if module is None:
            msg = f'there is no module for {persistence_interface_module_name=}. ' \
                  f'Have you defined the right name for the plugin? ' \
                  f'Or was there error in initialization of the plugin?'
            print(msg)
            raise BaseException(msg)
        else:
            return module.get_implementation()


