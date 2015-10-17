<?xml version="1.0" encoding="UTF-8" ?>
<!--
	Good Run List XSL-T
	Created by Morten Dam Jørgensen on 2011-05-29.
	Copyright (c) 2011 Niels Bohr Institute. All rights reserved.
-->

<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


	<xsl:output encoding="UTF-8" method="html" indent="yes" version="4.0"/>
    <xsl:template name="dots">

        <xsl:param name="count" select="1"/>

        <xsl:if test="$count > 0">
          <xsl:text>.</xsl:text>
          <xsl:call-template name="dots">
            <xsl:with-param name="count" select="$count - 1"/>
          </xsl:call-template>
        </xsl:if>

    </xsl:template>

	<xsl:template match="/">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
            <head>
                <link rel="stylesheet" href="grlstyle.css" type="text/css" charset="utf-8" />
                <script src="jquery.min.js" type="text/javascript" charset="utf-8"></script>
                <script src="grl_view.js" type="text/javascript" charset="utf-8"></script>
				
                <script language="javascript">
                    var grl={
                    <xsl:for-each select="LumiRangeCollection/NamedLumiRange">
                        "Name" : "<xsl:value-of select="Name"/>",
                        "Link" : "<xsl:value-of select="Link"/>",
                        "Delivered" : "<xsl:value-of select="Delivered"/>",
                        "Recorded" : "<xsl:value-of select="Recorded"/>",
                        "Version" : "<xsl:value-of select="Version"/>",
                        "Query" : "<xsl:value-of select="Metadata[@Name='Query']"/>",
                        "RunList" : "<xsl:value-of select="Metadata[@Name='RunList']"/>",
                        "RQTSVNVersion" :  "<xsl:value-of select="Metadata[@Name='RQTSVNVersion']"/>",
                        "StreamListInfo" : [
                        <xsl:for-each select="Metadata[@Name='StreamListInfo']/Stream">
                            {
                             "Name" : "<xsl:value-of select="@Name"/>",
                             "TotalNumOfEvents" : <xsl:value-of select="@TotalNumOfEvents"/>,
                             "NumOfSelectedEvents" : <xsl:value-of select="@NumOfSelectedEvents"/>
                            },
                        </xsl:for-each>
                        ],
                        "LumiBlockCollection" : [
                        <xsl:for-each select="LumiBlockCollection">
                            {
                            "Run" : <xsl:value-of select="Run"/>,
                            "Ranges" : [
                                  <xsl:for-each select="LBRange">
                                      {
                                      "Start" : <xsl:value-of select="@Start"/>,
                                      "End" : <xsl:value-of select="@End"/>
                                      },
                                  </xsl:for-each>
                            ]
                            },
                        </xsl:for-each>
                        ]

                    </xsl:for-each>
                    };	
                    
                    function start(){
                        var view = new GrlView(grl, $("#grl"));
                        view.header();
    				}
    				
                </script>
            </head>
          <body onload="start()">          
            <div id="grl">
                <xsl:for-each select="LumiRangeCollection/NamedLumiRange">
                    <h1><xsl:value-of select="Name"/> Good Run List</h1>
                    <h3>Query</h3><div id="query"><xsl:value-of select="Metadata[@Name='Query']"/></div><br/>
                    <h3>RunList</h3><xsl:value-of select="Metadata[@Name='RunList']"/><br/>
                    <h3>StreamListInfo</h3>
                    <xsl:for-each select="Metadata[@Name='StreamListInfo']/Stream">
                        
                         <xsl:value-of select="@Name"/>, TotalNumOfEvents : <xsl:value-of select="@TotalNumOfEvents"/>, NumOfSelectedEvents: <xsl:value-of select="@NumOfSelectedEvents"/><br/>
                    </xsl:for-each>
                    
                    <h1>Lumi blocks</h1>
                    <xsl:for-each select="LumiBlockCollection">
                        <h2><xsl:value-of select="Run"/></h2>
                        <xsl:call-template name="dots">
                             <xsl:with-param name="count" select="LBRange[last()]"/>
                           </xsl:call-template>
                        
                        <h1><xsl:value-of select="LBRange[0][@End]" /></h1>
                        <div class="range">
                              <xsl:for-each select="LBRange">
                                 LB : <xsl:value-of select="@Start"/>-<xsl:value-of select="@End"/>, 

                              </xsl:for-each>
                        </div>
                    </xsl:for-each>


                </xsl:for-each>
				
            </div>
          </body>
          </html>
          
	</xsl:template>
</xsl:stylesheet>
