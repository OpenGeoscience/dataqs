<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>gistemp1200_ersstv4</sld:Name>
    <sld:UserStyle>
      <sld:Name>gistemp1200_ersstv4</sld:Name>
      <sld:Title>gistemp1200_ersstv4</sld:Title>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
        <Opacity>1.0</Opacity>
        <ChannelSelection>
                <GrayChannel>
                        <SourceChannelName>{latest_band}</SourceChannelName>
                </GrayChannel>
        </ChannelSelection>
        <ColorMap extended="true">
            <sld:ColorMapEntry color="#2b83ba" label="&lt;= -7.5 °C" opacity="1.0" quantity="-750"/>
            <sld:ColorMapEntry color="#6bb0af" label="-5.0 °C" opacity="1.0" quantity="-500"/>
            <sld:ColorMapEntry color="#abdda4" label="-3.75 °C" opacity="1.0" quantity="-375"/>
            <sld:ColorMapEntry color="#d5eeb1" label="-1.5 °C" opacity="1.0" quantity="-150"/>
            <sld:ColorMapEntry color="#ffffbf" label="0 °C" opacity="1.0" quantity="0"/>
            <sld:ColorMapEntry color="#fed690" label="1.5 °C" opacity="1.0" quantity="150"/>
            <sld:ColorMapEntry color="#fdae61" label="3.75 °C" opacity="1.0" quantity="375"/>
            <sld:ColorMapEntry color="#ea633e" label="5.0 °C" opacity="1.0" quantity="500"/>
            <sld:ColorMapEntry color="#d7191c" label="&gt;= 75 °C" opacity="1.0" quantity="750"/>
            <sld:ColorMapEntry color="#FFFFFF" label="" opacity="0.0" quantity="32765"/>
        </ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>