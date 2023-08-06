library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_misc.all;
use ieee.numeric_std.all;

library work;
use work.Constants.all;
use work.Types.all;

entity BDTTopAxiStream is
generic(
  DATA_WIDTH_BYTES : integer := 4
);
port(
    clk           : in std_logic;
    -- axi stream in (features)
    s_axis_tdata  : in  std_logic_vector(8*DATA_WIDTH_BYTES-1 downto 0);
    s_axis_tvalid : in  std_logic;
    s_axis_tlast  : in std_logic; 
    s_axis_tready : out std_logic;
    -- axi stream out (predictions)
    m_axis_tdata  : out std_logic_vector(8*DATA_WIDTH_BYTES-1 downto 0);
    m_axis_tvalid : out std_logic;
    m_axis_tlast  : out std_logic;
    m_axis_tready : in  std_logic
);
end BDTTopAxiStream;

architecture rtl of BDTTopAxiStream is

  -- IO signals
  signal iX    : integer range 0 to nFeatures - 1 := 0;
  signal iY    : integer range 0 to nClasses - 1 := 0;
  signal y_int : tyArray(0 to nClasses - 1)   := (others => to_ty(0));
  signal read  : boolean := false;
  signal last  : boolean := false;

  -- BDT signals
  signal X     : txArray(0 to nFeatures - 1)  := (others => to_tx(0));
  signal X_vld : boolean                      := false;
  signal y     : tyArray(0 to nClasses - 1)   := (others => to_ty(0));
  signal y_vld : boolArray(0 to nClasses - 1) := (others => false);

begin

  -- Assumes nClasses < nFeatures for now (less data out than in)
  s_axis_tready <= m_axis_tready;

  IOProc:
  process(clk)
  begin
    if rising_edge(clk) then

      -- read the input stream (serial to parallel)
      if s_axis_tvalid = '1' then
        if iX = nFeatures - 1 then
          iX <= 0;
          X_vld <= true;
          if s_axis_tlast = '1' then
            last <= true;
          end if;
        else
          iX <= iX + 1;
          X_vld <= false;
        end if;
        X(iX) <= signed(s_axis_tdata(tX'HIGH-1 downto 0));
      end if;

      -- read the BDT output into internal buffer
      if y_vld(0) then
        y_int <= y;
        read <= true;
      end if;

      -- write the output buffer to the output stream (parallel to serial)
      if m_axis_tready = '1' and read then
        if iY = nClasses - 1 then
          iY <= 0;
          read <= false;
          if last then
            last <= false;
          end if;   
        else
          iY <= iY + 1;
        end if;
      end if;

    end if; -- if rising_edge(clk)
  end process;

  m_axis_tdata(tY'HIGH-1 downto 0) <= std_logic_vector(y_int(iY)) when read and m_axis_tready = '1' else (others => '0');
  m_axis_tvalid <= '1' when read and m_axis_tready = '1' else '0';
  m_axis_tlast <= '1' when read and m_axis_tready = '1' and iY = nClasses - 1 and last else '0';


  BDTInstance : entity work.BDTTop
  port map(
    clk   => clk,
    X     => X,
    X_vld => X_vld,
    y     => y,
    y_vld => y_vld
  );

end rtl;