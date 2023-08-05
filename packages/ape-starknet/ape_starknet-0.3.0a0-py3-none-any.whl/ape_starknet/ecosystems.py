from typing import Any, Dict, Iterator, List, Tuple, Type, Union

from ape.api import BlockAPI, EcosystemAPI, ReceiptAPI, TransactionAPI
from ape.contracts import ContractContainer
from ape.types import AddressType, ContractLog, RawAddress
from eth_utils import is_0x_prefixed
from ethpm_types import ContractType
from ethpm_types.abi import ConstructorABI, EventABI, MethodABI
from hexbytes import HexBytes
from starknet_py.net.models.address import parse_address  # type: ignore
from starknet_py.net.models.chains import StarknetChainId  # type: ignore
from starknet_py.utils.data_transformer import DataTransformer  # type: ignore
from starkware.starknet.definitions.fields import ContractAddressSalt  # type: ignore
from starkware.starknet.definitions.transaction_type import TransactionType  # type: ignore
from starkware.starknet.public.abi import get_selector_from_name  # type: ignore
from starkware.starknet.public.abi_structs import identifier_manager_from_abi  # type: ignore
from starkware.starknet.services.api.contract_class import ContractClass  # type: ignore

from ape_starknet.exceptions import StarknetEcosystemError
from ape_starknet.transactions import (
    ContractDeclaration,
    DeclareTransaction,
    DeployReceipt,
    DeployTransaction,
    InvocationReceipt,
    InvokeFunctionTransaction,
    StarknetTransaction,
)
from ape_starknet.utils import to_checksum_address

NETWORKS = {
    # chain_id, network_id
    "mainnet": (StarknetChainId.MAINNET.value, StarknetChainId.MAINNET.value),
    "testnet": (StarknetChainId.TESTNET.value, StarknetChainId.TESTNET.value),
}


class StarknetBlock(BlockAPI):
    """
    A block in Starknet.
    """


class Starknet(EcosystemAPI):
    """
    The Starknet ``EcosystemAPI`` implementation.
    """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    @classmethod
    def decode_address(cls, raw_address: RawAddress) -> AddressType:
        """
        Make a checksum address given a supported format.
        Borrowed from ``eth_utils.to_checksum_address()`` but supports
        non-length 42 addresses.

        Args:
            raw_address (Union[int, str, bytes]): The value to convert.

        Returns:
            ``AddressType``: The converted address.
        """
        return to_checksum_address(raw_address)

    @classmethod
    def encode_address(cls, address: AddressType) -> int:
        return parse_address(address)

    def serialize_transaction(self, transaction: TransactionAPI) -> bytes:
        if not isinstance(transaction, StarknetTransaction):
            raise StarknetEcosystemError(f"Can only serialize '{StarknetTransaction.__name__}'.")

        starknet_object = transaction.as_starknet_object()
        return starknet_object.deserialize()

    def decode_returndata(self, abi: MethodABI, raw_data: List[int]) -> List[Any]:  # type: ignore
        raw_data = [self.encode_primitive_value(v) if isinstance(v, str) else v for v in raw_data]

        def clear_lengths(arr):
            arr_len = arr[0]
            rest = arr[1:]
            num_rest = len(rest)
            return clear_lengths(rest) if arr_len == num_rest else arr

        is_arr = (
            len(abi.outputs) >= 2
            and abi.outputs[0].name == "arr_len"
            and abi.outputs[1].type == "felt*"
        )
        has_leftover_length = len(raw_data) > 1 and not is_arr
        if (
            len(abi.outputs) == 2
            and is_arr
            and len(raw_data) >= 2
            and all([isinstance(i, int) for i in raw_data])
        ) or has_leftover_length:
            # Is array - check if need to strip off arr_len
            return clear_lengths(raw_data)

        return raw_data

    def encode_calldata(
        self,
        full_abi: List,
        method_abi: Union[ConstructorABI, MethodABI],
        call_args: Union[List, Tuple],
    ) -> List:
        full_abi = [abi.dict() if hasattr(abi, "dict") else abi for abi in full_abi]
        id_manager = identifier_manager_from_abi(full_abi)
        transformer = DataTransformer(method_abi.dict(), id_manager)
        pre_encoded_args: List[Any] = []
        index = 0
        last_index = len(method_abi.inputs) - 1
        did_process_array_during_arr_len = False

        for call_arg, input_type in zip(call_args, method_abi.inputs):
            if str(input_type.type).endswith("*"):
                if did_process_array_during_arr_len:
                    did_process_array_during_arr_len = False
                    continue

                encoded_arg = self._pre_encode_value(call_arg)
                pre_encoded_args.append(encoded_arg)
            elif (
                input_type.name in ("arr_len", "call_array_len")
                and index < last_index
                and str(method_abi.inputs[index + 1].type).endswith("*")
            ):
                pre_encoded_arg = self._pre_encode_value(call_arg)

                if isinstance(pre_encoded_arg, int):
                    # 'arr_len' was provided.
                    array_index = index + 1
                    pre_encoded_array = self._pre_encode_array(call_args[array_index])
                    pre_encoded_args.append(pre_encoded_array)
                    did_process_array_during_arr_len = True
                else:
                    pre_encoded_args.append(pre_encoded_arg)

            else:
                pre_encoded_args.append(self._pre_encode_value(call_arg))

            index += 1

        encoded_calldata, _ = transformer.from_python(*pre_encoded_args)
        return encoded_calldata

    def _pre_encode_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return self._pre_encode_struct(value)
        elif isinstance(value, (list, tuple)):
            return self._pre_encode_array(value)
        else:
            return self.encode_primitive_value(value)

    def _pre_encode_array(self, array: Any) -> List:
        if not isinstance(array, (list, tuple)):
            # Will handle single item structs and felts.
            return self._pre_encode_array([array])

        encoded_array = []
        for item in array:
            encoded_value = self._pre_encode_value(item)
            encoded_array.append(encoded_value)

        return encoded_array

    def _pre_encode_struct(self, struct: Dict) -> Dict:
        encoded_struct = {}
        for key, value in struct.items():
            encoded_struct[key] = self._pre_encode_value(value)

        return encoded_struct

    def encode_primitive_value(self, value: Any) -> int:
        if isinstance(value, int):
            return value

        elif isinstance(value, str) and is_0x_prefixed(value):
            return int(value, 16)

        elif isinstance(value, HexBytes):
            return int(value.hex(), 16)

        return value

    def decode_receipt(self, data: dict) -> ReceiptAPI:
        txn_type = TransactionType(data["type"])
        cls: Union[Type[ContractDeclaration], Type[DeployReceipt], Type[InvocationReceipt]]
        if txn_type == TransactionType.INVOKE_FUNCTION:
            cls = InvocationReceipt
        elif txn_type == TransactionType.DEPLOY:
            cls = DeployReceipt
        elif txn_type == TransactionType.DECLARE:
            cls = ContractDeclaration
        else:
            raise ValueError(f"Unable to handle contract type '{txn_type.value}'.")

        return cls.parse_obj(data)

    def decode_block(self, data: dict) -> BlockAPI:
        return StarknetBlock(
            hash=HexBytes(data["block_hash"]),
            number=data["block_number"],
            parentHash=HexBytes(data["parent_block_hash"]),
            size=len(data["transactions"]),  # TODO: Figure out size
            timestamp=data["timestamp"],
        )

    def encode_deployment(
        self, deployment_bytecode: HexBytes, abi: ConstructorABI, *args, **kwargs
    ) -> TransactionAPI:
        salt = kwargs.get("salt")
        if not salt:
            salt = ContractAddressSalt.get_random_value()

        constructor_args = list(args)
        contract = ContractClass.deserialize(deployment_bytecode)
        calldata = self.encode_calldata(contract.abi, abi, constructor_args)
        return DeployTransaction(
            salt=salt,
            constructor_calldata=calldata,
            contract_code=contract.dumps(),
            token=kwargs.get("token"),
        )

    def encode_transaction(
        self, address: AddressType, abi: MethodABI, *args, **kwargs
    ) -> TransactionAPI:
        # NOTE: This method only works for invoke-transactions
        contract_type = self.chain_manager.contracts[address]
        encoded_calldata = self.encode_calldata(contract_type.abi, abi, list(args))

        return InvokeFunctionTransaction(
            contract_address=address,
            method_abi=abi,
            calldata=encoded_calldata,
            sender=kwargs.get("sender"),
            max_fee=kwargs.get("max_fee", 0),
        )

    def encode_contract_declaration(
        self, contract: Union[ContractContainer, ContractType], *args, **kwargs
    ) -> DeclareTransaction:
        contract_type = (
            contract.contract_type if isinstance(contract, ContractContainer) else contract
        )
        code = (
            (contract_type.deployment_bytecode.bytecode or 0)
            if contract_type.deployment_bytecode
            else 0
        )
        starknet_contract = ContractClass.deserialize(HexBytes(code))
        return DeclareTransaction(contract_type=contract_type, data=starknet_contract.dumps())

    def create_transaction(self, **kwargs) -> TransactionAPI:
        txn_type = TransactionType(kwargs.pop("type", kwargs.pop("tx_type", "")))
        txn_cls: Union[
            Type[InvokeFunctionTransaction], Type[DeployTransaction], Type[DeclareTransaction]
        ]
        invoking = txn_type == TransactionType.INVOKE_FUNCTION
        if invoking:
            txn_cls = InvokeFunctionTransaction
        elif txn_type == TransactionType.DEPLOY:
            txn_cls = DeployTransaction
        elif txn_type == TransactionType.DECLARE:
            txn_cls = DeclareTransaction

        txn_data: Dict[str, Any] = {**kwargs, "signature": None}
        if "chain_id" not in txn_data and self.network_manager.active_provider:
            txn_data["chain_id"] = self.provider.chain_id

        # For deploy-txns, 'contract_address' is the address of the newly deployed contract.
        if "contract_address" in txn_data:
            txn_data["contract_address"] = self.decode_address(txn_data["contract_address"])

        if not invoking:
            return txn_cls(**txn_data)

        """ ~ Invoke transactions ~ """

        if "method_abi" not in txn_data:
            contract_int = txn_data["contract_address"]
            contract_str = self.decode_address(contract_int)
            contract = self.chain_manager.contracts.get(contract_str)
            if not contract:
                raise ValueError("Unable to create transaction objects from other networks.")

            selector = txn_data["entry_point_selector"]
            if isinstance(selector, str):
                selector = int(selector, 16)

            for abi in contract.mutable_methods:
                selector_to_check = get_selector_from_name(abi.name)

                if selector == selector_to_check:
                    txn_data["method_abi"] = abi

        if "calldata" in txn_data and txn_data["calldata"] is not None:
            # Transactions in blocks show calldata as flattened hex-strs
            # but elsewhere we expect flattened ints. Convert to ints for
            # consistency and testing purposes.
            encoded_calldata = [self.encode_primitive_value(v) for v in txn_data["calldata"]]
            txn_data["calldata"] = encoded_calldata

        return txn_cls(**txn_data)

    def decode_logs(self, abi: EventABI, raw_logs: List[Dict]) -> Iterator[ContractLog]:
        for index, log in enumerate(raw_logs):
            event_args = dict(zip([a.name for a in abi.inputs], log["data"]))
            yield ContractLog(  # type: ignore
                name=abi.name,
                index=index,
                event_arguments=event_args,
                transaction_hash=log["transaction_hash"],
                block_hash=log["block_hash"],
                block_number=log["block_number"],
            )
