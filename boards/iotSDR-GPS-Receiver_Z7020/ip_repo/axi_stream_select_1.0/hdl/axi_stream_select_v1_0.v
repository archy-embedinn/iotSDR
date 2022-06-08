
`timescale 1 ns / 1 ps

	module axi_stream_select_v1_0 #
	(
		// Users to add parameters here

		// User parameters ends
		// Do not modify the parameters beyond this line


		// Parameters of Axi Slave Bus Interface S00_AXIS
		parameter integer C_S00_AXIS_TDATA_WIDTH	= 32,

		// Parameters of Axi Slave Bus Interface S01_AXIS
		parameter integer C_S01_AXIS_TDATA_WIDTH	= 32,

		// Parameters of Axi Master Bus Interface M00_AXIS
		parameter integer C_M00_AXIS_TDATA_WIDTH	= 32,
		parameter integer C_M00_AXIS_START_COUNT	= 32
	)
	(
		// Users to add ports here
		input wire  select_axis_slave,

		// User ports ends
		// Do not modify the ports beyond this line


		// Ports of Axi Slave Bus Interface S00_AXIS
		input wire  s00_axis_aclk,
		input wire  s00_axis_aresetn,
		output reg  s00_axis_tready,
		input wire [C_S00_AXIS_TDATA_WIDTH-1 : 0] s00_axis_tdata,
		input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1 : 0] s00_axis_tstrb,
		input wire  s00_axis_tlast,
		input wire  s00_axis_tvalid,

		// Ports of Axi Slave Bus Interface S01_AXIS
		input wire  s01_axis_aclk,
		input wire  s01_axis_aresetn,
		output reg  s01_axis_tready,
		input wire [C_S01_AXIS_TDATA_WIDTH-1 : 0] s01_axis_tdata,
		input wire [(C_S01_AXIS_TDATA_WIDTH/8)-1 : 0] s01_axis_tstrb,
		input wire  s01_axis_tlast,
		input wire  s01_axis_tvalid,

		// Ports of Axi Master Bus Interface M00_AXIS
		input wire  m00_axis_aclk,
		input wire  m00_axis_aresetn,
		output reg  m00_axis_tvalid,
		output reg [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata,
		output reg [(C_M00_AXIS_TDATA_WIDTH/8)-1 : 0] m00_axis_tstrb,
		output reg  m00_axis_tlast,
		input wire  m00_axis_tready
	);

	// Add user logic here
    
    always@(*) begin
    
        if(select_axis_slave) begin
            m00_axis_tvalid	= s01_axis_tvalid;
	        m00_axis_tdata	= s01_axis_tdata;
	        m00_axis_tlast	= s01_axis_tlast;
	        m00_axis_tstrb	= {(C_M00_AXIS_TDATA_WIDTH/8){1'b1}};
	        
	        s01_axis_tready = m00_axis_tready;
        end

        else begin
            m00_axis_tvalid	= s00_axis_tvalid;
	        m00_axis_tdata	= s00_axis_tdata;
	        m00_axis_tlast	= s00_axis_tlast;
	        m00_axis_tstrb	= {(C_M00_AXIS_TDATA_WIDTH/8){1'b1}};
	        
	        s00_axis_tready = m00_axis_tready;
        end
    
    
    end
	// User logic ends

	endmodule
