# -*- coding: utf-8 -*-
"""Deserialize PUS Service 1 Verification TM
"""
from __future__ import annotations

import enum
import struct

from spacepackets.ccsds.spacepacket import PacketId, PacketSeqCtrl
from spacepackets.ccsds.time import CdsShortTimestamp
from spacepackets.ecss.definitions import PusServices
from spacepackets.ecss.tm import PusVersion, PusTelemetry
from spacepackets.log import get_console_logger


class Subservices(enum.IntEnum):
    TM_ACCEPTANCE_SUCCESS = 1
    TM_ACCEPTANCE_FAILURE = 2
    TM_START_SUCCESS = 3
    TM_START_FAILURE = 4
    TM_STEP_SUCCESS = 5
    TM_STEP_FAILURE = 6
    TM_COMPLETION_SUCCESS = 7
    TM_COMPLETION_FAILURE = 8


class RequestId:
    def __init__(
        self, tc_packet_id: PacketId, tc_psc: PacketSeqCtrl, ccsds_version: int = 0b000
    ):
        self.tc_packet_id = tc_packet_id
        self.tc_psc = tc_psc
        self.ccsds_version = ccsds_version

    @classmethod
    def empty(cls):
        return cls(PacketId.empty(), PacketSeqCtrl.empty())

    @classmethod
    def from_raw(cls, tm_data: bytes) -> RequestId:
        if len(tm_data) < 4:
            raise ValueError(
                "Given Raw TM data too small to parse Request ID. Must be 4 bytes at least"
            )
        packet_id_version_raw = struct.unpack("!H", tm_data[0:2])[0]
        psc_raw = struct.unpack("!H", tm_data[2:4])[0]
        return cls(
            ccsds_version=(packet_id_version_raw >> 13) & 0b111,
            tc_packet_id=PacketId.from_raw(packet_id_version_raw),
            tc_psc=PacketSeqCtrl.from_raw(psc_raw),
        )

    def pack(self) -> bytes:
        raw = bytearray()
        packet_id_and_version = (self.ccsds_version << 13) | self.tc_packet_id.raw()
        raw.extend(struct.pack("!H", packet_id_and_version))
        raw.extend(struct.pack("!H", self.tc_psc.raw()))
        return raw


class Service1Tm:
    """Service 1 TM class representation. Can be used to deserialize raw service 1 packets."""

    def __init__(
        self,
        subservice: int,
        tc_request_id: RequestId,
        time: CdsShortTimestamp = None,
        ssc: int = 0,
        apid: int = -1,
        packet_version: int = 0b000,
        pus_version: PusVersion = PusVersion.GLOBAL_CONFIG,
        secondary_header_flag: bool = True,
        space_time_ref: int = 0b0000,
        destination_id: int = 0,
    ):
        self.pus_tm = PusTelemetry(
            service=PusServices.S1_VERIFICATION,
            subservice=subservice,
            time=time,
            ssc=ssc,
            source_data=bytearray(tc_request_id.pack()),
            apid=apid,
            packet_version=packet_version,
            pus_version=pus_version,
            secondary_header_flag=secondary_header_flag,
            space_time_ref=space_time_ref,
            destination_id=destination_id,
        )
        self._has_tc_error_code = False
        self._is_step_reply = False
        # Failure Reports with error code
        self._error_code = 0
        self._step_number = 0
        self._error_param1 = -1
        self._error_param2 = -1
        self._tc_req_id = tc_request_id

    def pack(self) -> bytearray:
        return self.pus_tm.pack()

    @classmethod
    def __empty(cls) -> Service1Tm:
        return cls(subservice=0, tc_request_id=RequestId.empty())

    @classmethod
    def unpack(
        cls,
        raw_telemetry: bytearray,
        pus_version: PusVersion = PusVersion.GLOBAL_CONFIG,
    ) -> Service1Tm:
        """Parse a service 1 telemetry packet

        :param raw_telemetry:
        :param pus_version:
        :raises ValueError: Raw telemetry too short
        :return:
        """
        service_1_tm = cls.__empty()
        service_1_tm.pus_tm = PusTelemetry.unpack(
            raw_telemetry=raw_telemetry, pus_version=pus_version
        )
        cls._unpack_raw_tm(service_1_tm)
        return service_1_tm

    @classmethod
    def _unpack_raw_tm(cls, instance: Service1Tm):
        tm_data = instance.pus_tm.tm_data
        if len(tm_data) < 4:
            raise ValueError("TM data less than 4 bytes")
        instance.tc_req_id = RequestId.from_raw(tm_data[0:4])
        if instance.pus_tm.subservice % 2 == 0:
            instance._handle_failure_verification()
        else:
            instance._handle_success_verification()

    def _handle_failure_verification(self):
        """Handle parsing a verification failure packet, subservice ID 2, 4, 6 or 8"""
        self._has_tc_error_code = True
        tm_data = self.pus_tm.tm_data
        subservice = self.pus_tm.subservice
        expected_len = 14
        if subservice == 6:
            self._is_step_reply = True
            expected_len = 15
        elif subservice not in [2, 4, 8]:
            logger = get_console_logger()
            logger.error("Service1TM: Invalid subservice")
        if len(tm_data) < expected_len:
            logger = get_console_logger()
            logger.warning(
                f"PUS TM[1,{subservice}] source data smaller than expected 15 bytes"
            )
            raise ValueError
        current_idx = 4
        if self.is_step_reply:
            self._step_number = struct.unpack(
                ">B", tm_data[current_idx : current_idx + 1]
            )[0]
            current_idx += 1
        self._error_code = struct.unpack(">H", tm_data[current_idx : current_idx + 2])[
            0
        ]
        current_idx += 2
        self._error_param1 = struct.unpack(
            ">I", tm_data[current_idx : current_idx + 4]
        )[0]
        current_idx += 2
        self._error_param2 = struct.unpack(
            ">I", tm_data[current_idx : current_idx + 4]
        )[0]

    def _handle_success_verification(self):
        if self.pus_tm.subservice == 5:
            self._is_step_reply = True
            self._step_number = struct.unpack(">B", self.pus_tm.tm_data[4:5])[0]
        elif self.pus_tm.subservice not in [1, 3, 7]:
            logger = get_console_logger()
            logger.warning("Service1TM: Invalid subservice")

    @property
    def error_param_1(self) -> int:
        """Returns -1 if the packet does not have a failure code"""
        if not self._has_tc_error_code:
            return -1
        else:
            return self._error_param1

    @property
    def error_param_2(self) -> int:
        if not self._has_tc_error_code:
            return -1
        else:
            return self._error_param2

    @property
    def is_step_reply(self):
        return self._is_step_reply

    @property
    def has_tc_error_code(self):
        return self._has_tc_error_code

    @property
    def tc_req_id(self):
        return self._tc_req_id

    @tc_req_id.setter
    def tc_req_id(self, value):
        self._tc_req_id = value

    @property
    def error_code(self):
        if self._has_tc_error_code:
            return self._error_code
        else:
            logger = get_console_logger()
            logger.warning("This is not a failure packet, returning 0")
            return 0

    @property
    def step_number(self):
        if self._is_step_reply:
            return self._step_number
        else:
            logger = get_console_logger()
            logger.warning("This is not a step reply, returning 0")
            return 0
