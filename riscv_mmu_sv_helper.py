import gdb

class Register :
    """
    Helper to access register bitfield

    >>> reg = Register(0x80000000000812d0)
    >>> hex(reg.get_bitfield(60, 4))
    '0x8'
    >>> hex(reg.get_bitfield(0, 44))
    '0x812d0'
    >>> reg.set_bitfield(60, 4, 9)
    >>> hex(reg.value)
    '0x90000000000812d0'
    >>> reg.set_bitfield(0, 44, 0x1A15d6)
    >>> hex(reg.value)
    '0x90000000001a15d6'
    """
    def __init__(self, value):
        self.value = int(value) & 0xffffffffffffffff

    def get_bitfield(self, bitIdx, size):
        """get bitfield value of a register

        Args:
            bitIdx ([integer]): least signifiant bit of the bitfield to get in
                                register
            size ([integer]): size of the bitfield to get

        Returns:
            [integer]: the data field that start at bit 'bitIdx' index of length
            'size'
        """
        mask = (1 << size) - 1
        val = (self.value & (mask << bitIdx)) >> bitIdx
        return (val)

    def set_bitfield(self, bitIdx, size, value):
        """get bitfield value of a register

        Args:
            bitIdx ([integer]): least signifiant bit of the bitfield to set in
                                register
            size ([integer]): [description]
            value ([integer]): [description]
        """
        mask = (1 << size) - 1
        self.value = self.value & ~(mask << bitIdx)
        bitfield = (value & mask) << bitIdx
        self.value = self.value | bitfield

class VAddrTranslate(gdb.Command):
    """Print translated address form virtual memory"""
    PPNSIZE = 44

    def _read_phy_memory(self, address, length):
        current_inferior = gdb.selected_inferior ()
        satp = Register(gdb.parse_and_eval("$satp"))
        previous_mode = satp.get_bitfield(60, 4)

        satp.set_bitfield(60, 4, 0)
        gdb.execute("set $satp =" + hex(satp.value))

        try:
            value = current_inferior.read_memory(address, length)
        finally:
            satp.set_bitfield(60, 4, previous_mode)
            gdb.execute("set $satp =" + hex(satp.value))

        return(value)

    def _translate_SVXX(self, vAddr, PTESize, levels,
                        pageSize, VPNSize, VASize, ppnLengths):
        # valid for RV64
        satp = Register(gdb.parse_and_eval("$satp"))
        ppn = satp.get_bitfield(0, self.PPNSIZE)
        asid = satp.get_bitfield(self.PPNSIZE, 16)
        mode = satp.get_bitfield(60, 4)

        if mode == 0 :
            print("No translation or protection")
            return

        vpn = []
        vAddr = Register(vAddr)
        for i in range(levels):
            vpn.append(vAddr.get_bitfield(12 + i * VPNSize, VPNSize))

        #step 1
        i = levels - 1
        a = ppn * pageSize

        while (i >= 0) :
            # step 2
            pte_val = self._read_phy_memory(a + vpn[i] * PTESize, 8)
            pte_val = int.from_bytes(pte_val, "little", signed=False)
            pte = Register(pte_val)
            # step 3
            pte_v = pte.get_bitfield(0,1)
            pte_r = pte.get_bitfield(1,1)
            pte_w = pte.get_bitfield(2,1)
            pte_x = pte.get_bitfield(3,1)
            if (pte_v == 0) or (pte_r == 0 and pte_w == 1) :
                print("error page-fault should have been raised\n")
                return None

            # step 4
            if (pte_r == 1) or (pte_x == 1) :
                break
            else :
                i = i - 1
                if i < 0 :
                    print("error page-fault should have been raised\n")
                    return
                else :
                    a = pte.get_bitfield(10,44) * pageSize

        # step 5 : print access rights
        print("access rights: " + "r:" + str(pte_r) + 
              " w:" + str(pte_w) + " x:" + str(pte_x))

        # step 6 check missaligned
        if (i > 0) and pte.get_bitfield(10, i * 9) != 0:
            print("error page-fault should be raised: misaligned superpage\n")
            return

        # cannot do step 7 checks

        pAddr = Register(0)
        # add offset
        pAddr.set_bitfield(0,12, vAddr.get_bitfield(0,12))

        if i > 0 :
            va_vpn = vAddr.get_bitfield(12, 9 * i)
            pAddr.set_bitfield(12, 9 * i, va_vpn)

        pAddr.set_bitfield(12 + sum(ppnLengths[0:i]),
                           sum(ppnLengths[i:levels]),
                           pte.get_bitfield(10 + sum(ppnLengths[0:i]),
                                            sum(ppnLengths[i:levels])))

        print("pAddr: " + hex(pAddr.value))

class SV39AddrTranslate(VAddrTranslate):
    """Print translated address form virtual memory"""

    def __init__(self):
        super(SV39AddrTranslate, self).__init__(
            "sv39translate",
            gdb.COMMAND_USER
        )

    def _translate_SV39(self, vAddr):
        PTESIZE = 8
        LEVELS = 3
        PAGESIZE = 4096
        VPNSIZE = 9
        VASIZE = 39
        PPNLENGTHS = [9,9,26]

        self._translate_SVXX(vAddr, PTESIZE, LEVELS,
                            PAGESIZE, VPNSIZE, VASIZE, PPNLENGTHS)

    def invoke(self, args, from_tty):
        addr = int(gdb.parse_and_eval(args))
        self._translate_SV39(addr)

class SV48AddrTranslate(VAddrTranslate):
    """Print translated address form virtual memory"""

    def __init__(self):
        super(SV48AddrTranslate, self).__init__(
            "sv48translate",
            gdb.COMMAND_USER
        )

    def _translate_SV48(self, vAddr):
        PTESIZE = 8
        LEVELS = 4
        PAGESIZE = 4096
        VPNSIZE = 9
        VASIZE = 48
        PPNLENGTHS = [9,9,9,17]

        self._translate_SVXX(vAddr, PTESIZE, LEVELS,
                            PAGESIZE, VPNSIZE, VASIZE, PPNLENGTHS)

    def invoke(self, args, from_tty):
        addr = int(gdb.parse_and_eval(args))
        self._translate_SV48(addr)

SV39AddrTranslate()
SV48AddrTranslate()
